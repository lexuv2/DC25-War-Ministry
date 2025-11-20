package com.backend.Gmail;

import com.backend.cv.dto.CvDto;
import com.backend.cv.entity.CV;
import com.backend.cv.service.api.CVService;
import com.fasterxml.jackson.databind.DeserializationFeature;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.datatype.jsr310.JavaTimeModule;
import com.google.api.client.auth.oauth2.Credential;
import com.google.api.client.googleapis.auth.oauth2.GoogleAuthorizationCodeFlow;
import com.google.api.client.googleapis.auth.oauth2.GoogleClientSecrets;
import com.google.api.client.googleapis.javanet.GoogleNetHttpTransport;
import com.google.api.client.googleapis.json.GoogleJsonError;
import com.google.api.client.googleapis.json.GoogleJsonResponseException;
import com.google.api.client.http.AbstractInputStreamContent;
import com.google.api.client.http.ByteArrayContent;
import com.google.api.client.http.javanet.NetHttpTransport;
import com.google.api.client.json.JsonFactory;
import com.google.api.client.json.gson.GsonFactory;
import com.google.api.client.util.store.FileDataStoreFactory;
import com.google.api.services.gmail.Gmail;
import com.google.api.services.gmail.GmailScopes;
import com.google.api.services.gmail.model.*;
import com.google.api.services.gmail.model.Message;
import org.apache.commons.codec.binary.Base64;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.autoconfigure.context.ConfigurationPropertiesAutoConfiguration;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.stereotype.Service;
import com.google.api.services.drive.Drive;
import com.google.api.services.drive.DriveScopes;
import com.google.api.services.drive.model.File;

import jakarta.mail.*;
import jakarta.mail.internet.*;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.multipart.MultipartFile;

import java.io.*;
import java.nio.file.Files;
import java.security.GeneralSecurityException;
import java.util.*;

@Service
public class GmailService {
    private static final String APPLICATION_NAME = "DokumentyCyfrowe25";
    private static final JsonFactory JSON_FACTORY = GsonFactory.getDefaultInstance();
    private static final String TOKENS_DIRECTORY_PATH = "./tokens";

    private static final List<String> SCOPES = List.of(GmailScopes.GMAIL_READONLY, GmailScopes.GMAIL_LABELS, GmailScopes.GMAIL_COMPOSE, GmailScopes.GMAIL_SEND, GmailScopes.GMAIL_MODIFY, DriveScopes.DRIVE);
    private static final String CREDENTIALS_FILE_PATH = "/client_secret_270311492495-ip027ghqo1181v4qd288vv2203rjnu5v.apps.googleusercontent.com.json";

    private final GmailRepository gmailRepository;
    private final CVService cvService;
    private final ConfigurationPropertiesAutoConfiguration configurationPropertiesAutoConfiguration;

    // parserowe rzeczy
    String projectRoot = new java.io.File(System.getProperty("user.dir")).getPath();
    java.io.File parserDir = new java.io.File(projectRoot, "parser");
    // Ścieżka do Pythona w wirtualnym środowisku
    String pythonExecutable = new java.io.File(parserDir, "venv/Scripts/python").getAbsolutePath();
    // Skrypt główny
    String parserScript = new java.io.File(parserDir, "__main__.py").getAbsolutePath();

    @Autowired
    public GmailService(GmailRepository gmailRepository, CVService cvService, ConfigurationPropertiesAutoConfiguration configurationPropertiesAutoConfiguration) {
        this.gmailRepository = gmailRepository;
        this.cvService = cvService;
        this.configurationPropertiesAutoConfiguration = configurationPropertiesAutoConfiguration;
    }

    public Gmail getGmailService() throws IOException, GeneralSecurityException {
        final NetHttpTransport httpTransport = GoogleNetHttpTransport.newTrustedTransport();
        Credential credential = getGmailCredentials(httpTransport);
        return new Gmail.Builder(httpTransport, JSON_FACTORY, credential)
                .setApplicationName(APPLICATION_NAME)
                .build();
    }

    public Drive getDriveService() throws IOException, GeneralSecurityException {
        final var httpTransport = GoogleNetHttpTransport.newTrustedTransport();
        Credential credential = getGmailCredentials(httpTransport);
        return new Drive.Builder(httpTransport, JSON_FACTORY, credential)
                .setApplicationName(APPLICATION_NAME)
                .build();
    }

    private Credential getGmailCredentials(final com.google.api.client.http.javanet.NetHttpTransport httpTransport)
            throws IOException {
        InputStream in = getClass().getResourceAsStream(CREDENTIALS_FILE_PATH);
        if (in == null) {
            throw new FileNotFoundException("Resource not found: " + CREDENTIALS_FILE_PATH);
        }
        GoogleClientSecrets clientSecrets =
                GoogleClientSecrets.load(JSON_FACTORY, new InputStreamReader(in));

        GoogleAuthorizationCodeFlow flow = new GoogleAuthorizationCodeFlow.Builder(
                httpTransport, JSON_FACTORY, clientSecrets, SCOPES)
                .setDataStoreFactory(new FileDataStoreFactory(new java.io.File(TOKENS_DIRECTORY_PATH)))
                .setAccessType("offline")
                .build();

        var receiver = new com.google.api.client.extensions.jetty.auth.oauth2.LocalServerReceiver.Builder()
                .setPort(8888)
                .build();

        return new com.google.api.client.extensions.java6.auth.oauth2.AuthorizationCodeInstalledApp(flow, receiver)
                .authorize("user");
    }

    public void refreshAllEmails() throws IOException, GeneralSecurityException, InterruptedException {
        System.out.println(new java.io.File(System.getProperty("user.dir")).getParent());

        int numberOfEmails = getInboxMessageCount();

        Gmail service = getGmailService();

        // Get list of messages (ordered newest first)
        ListMessagesResponse response = service.users().messages()
                .list("me")
                .setLabelIds(List.of("INBOX"))
                .setMaxResults((long) (numberOfEmails + 1))
                .execute();

        List<Message> messages = response.getMessages();

        for (int index = 0; index < numberOfEmails; index++) {
            String messageId = messages.get(index).getId();

            if (!checkIfWasHandled(messageId)) {

                Message message = service.users().messages().get("me", messageId).setFormat("full").execute();

                // Extract basic info
                MessagePart payload = message.getPayload();
                List<MessagePartHeader> headers = payload.getHeaders();
                //String subject = getHeader(headers, "Subject");
                String from = getHeader(headers, "From");

                //tworzy nowy obiekt zawierajacy tylko id wiadomosci, adres mailowy i od razu ustawia wasHandled na true
                GmailEntity gmailEntity = new GmailEntity();
                gmailEntity.setMessageId(messageId);
                gmailEntity.setEmailAddress(from);
                gmailEntity.setWasHandled(true);
                gmailRepository.save(gmailEntity);

                List<Map<String, String>> attachments = new ArrayList<>();

                extractAttachments(service, "me", message.getPayload(), messageId, attachments);

                // Add attachment entries (base64-encoded)
                for (int i = 0; i < attachments.size(); i++) {
                    Map<String, String> entries = attachments.get(i);
                    for (Map.Entry<String, String> entry : entries.entrySet()) {
                        //TODO PARSE AND SAVE CANDIDATE DATA
                        File file = uploadAttachmentToDrive(entry);

                        byte[] decodedBytes = Base64.decodeBase64(entry.getValue());

                        MultipartFile multipartFile = new MultipartFile() {
                            @Override
                            public String getName() { return file.getName(); }

                            @Override
                            public String getOriginalFilename() { return file.getName(); }

                            @Override
                            public String getContentType() { return file.getMimeType(); }

                            @Override
                            public boolean isEmpty() { return decodedBytes.length == 0; }

                            @Override
                            public long getSize() { return decodedBytes.length; }

                            @Override
                            public byte[] getBytes() { return decodedBytes; }

                            @Override
                            public InputStream getInputStream() {
                                return new ByteArrayInputStream(decodedBytes);
                            }

                            @Override
                            public void transferTo(java.io.File dest) throws IOException {
                                Files.write(dest.toPath(), decodedBytes);
                            }
                        };

                        parsePdf(multipartFile);
                    }
                }

            }
        }
    }

    //to jest zdecydowanie do poprawy ale nie wiem jak to lepiej ogarnąć
    public void parsePdf(MultipartFile file) throws IOException, InterruptedException {
        // Zapisz plik tymczasowo
        java.io.File inputFile = java.io.File.createTempFile("input-", ".pdf");
        java.io.File inputFile2 = new java.io.File("test.pdf");
        file.transferTo(inputFile);
        file.transferTo(inputFile2);

        java.io.File outputFile = java.io.File.createTempFile("output-", ".json");

        // Budowa komendy
        ProcessBuilder processBuilder = new ProcessBuilder(
                pythonExecutable,
                parserScript,
                //"--api-mock",
                "--input", inputFile.getAbsolutePath(),
                "--output", outputFile.getAbsolutePath()
        );

        // Katalog roboczy parsera (tam, gdzie jest setup.py itd.)
        processBuilder.directory(new java.io.File(parserDir.getAbsolutePath()));
        processBuilder.redirectErrorStream(true);

        // Uruchom proces
        Process process = processBuilder.start();

        // Czytaj ewentualny output Pythona (np. logi)
        try (BufferedReader reader = new BufferedReader(new InputStreamReader(process.getInputStream()))) {
            reader.lines().forEach(System.out::println);
        }

        int exitCode = process.waitFor();
        if (exitCode != 0) {
            throw new RuntimeException("Parser error");
        }

        // Wczytaj wynik JSON
        String resultJson = Files.readString(outputFile.toPath());

//        // Sprzątanie (opcjonalne)
//        inputFile.delete();
//        outputFile.delete();

        ObjectMapper mapper = new ObjectMapper()
                .registerModule(new JavaTimeModule())
                .configure(DeserializationFeature.FAIL_ON_UNKNOWN_PROPERTIES, false);
        CvDto dto = mapper.readValue(resultJson, CvDto.class);
        CV cv = cvService.processCV(dto);
        System.out.println(cv.getFullName());
    }

    public int getInboxMessageCount() throws IOException, GeneralSecurityException {
        Gmail service = getGmailService();
        ListMessagesResponse response = service.users().messages().list("me").setLabelIds(List.of("INBOX")).execute();

        int total = 0;
        while (response.getMessages() != null) {
            total += response.getMessages().size();
            if (response.getNextPageToken() != null) {
                response = service.users().messages()
                        .list("me")
                        .setLabelIds(List.of("INBOX"))
                        .setPageToken(response.getNextPageToken())
                        .execute();
            } else {
                break;
            }
        }
        return total;
    }


    // TODO WYJEBAC KIEDYS
    public Map<String, String> getNthNewestMail(int index) throws IOException, GeneralSecurityException {
        Gmail service = getGmailService();

        // Get list of messages (ordered newest first)
        ListMessagesResponse response = service.users().messages()
                .list("me")
                .setLabelIds(List.of("INBOX"))
                .setMaxResults((long) (index + 1))
                .execute();

        List<Message> messages = response.getMessages();
        if (messages == null || messages.size() <= index) {
            throw new IllegalArgumentException("Not enough messages in inbox.");
        }

        String messageId = messages.get(index).getId();
        System.out.println(messageId);
        Message message = service.users().messages().get("me", messageId).setFormat("full").execute();

        // Extract basic info
        MessagePart payload = message.getPayload();
        List<MessagePartHeader> headers = payload.getHeaders();
        String subject = getHeader(headers, "Subject");
        String from = getHeader(headers, "From");
        String date = getHeader(headers, "Date");

        // TODO CHECK IF MAIL IN REPO

        String snippet = message.getSnippet();
        List<Map<String, String>> attachments = new ArrayList<>();

        extractAttachments(service, "me", message.getPayload(), messageId, attachments);

        Map<String, String> result = new HashMap<>();
        result.put("id", messageId);
        result.put("from", from);
        result.put("subject", subject);
        result.put("date", date);
        result.put("snippet", snippet);

// Add attachment entries (base64-encoded)
        for (int i = 0; i < attachments.size(); i++) {
            Map<String, String> entries = attachments.get(i);
            for (Map.Entry<String, String> entry : entries.entrySet()) {
                uploadAttachmentToDrive(entry);
                result.put("attachment_" + (i + 1) + "_filename", entry.getKey());
                result.put("attachment_" + (i + 1) + "_data", entry.getValue());
            }
        }

        //tworzy nowy obiekt zawierajacy tylko id wiadomosci, adres mailowy i od razu ustawia wasHandled na true
        GmailEntity gmailEntity = new GmailEntity();
        gmailEntity.setMessageId(messageId);
        gmailEntity.setEmailAddress(from);
        gmailEntity.setWasHandled(true);
        gmailRepository.save(gmailEntity);


        return result;
    }

    private void extractAttachments(Gmail service, String userId, MessagePart part, String messageId, List<Map<String, String>> attachments) throws IOException {
        if (part.getFilename() != null && !part.getFilename().isEmpty()) {
            String filename = part.getFilename().toLowerCase();
            if (filename.endsWith(".pdf") || filename.endsWith(".docx")) {
                String attachmentId = part.getBody().getAttachmentId();
                if (attachmentId != null) {
                    MessagePartBody attachPart = service.users().messages().attachments()
                            .get(userId, messageId, attachmentId)
                            .execute();

//                    byte[] fileData = Base64.decodeBase64(attachPart.getData());
//                    String base64 = Base64.encodeBase64String(fileData);

                    attachments.add(Map.of(
                            filename, attachPart.getData()
                    ));
                }
            }
        }

        if (part.getParts() != null) {
            for (MessagePart subPart : part.getParts()) {
                extractAttachments(service, userId, subPart, messageId, attachments);
            }
        }
    }

    private String getHeader(List<MessagePartHeader> headers, String name) {
        return headers.stream()
                .filter(h -> h.getName().equalsIgnoreCase(name))
                .map(MessagePartHeader::getValue)
                .findFirst()
                .orElse("(unknown)");
    }

    public File uploadAttachmentToDrive(Map.Entry<String, String> attachment
    ) throws IOException, GeneralSecurityException {

        // Extract filename and decode base64 content
        String filename = attachment.getKey();
        byte[] fileData = Base64.decodeBase64(attachment.getValue());

        // Automatically determine MIME type based on file extension
        String mimeType;
        if (filename.toLowerCase().endsWith(".pdf")) {
            mimeType = "application/pdf";
        } else if (filename.toLowerCase().endsWith(".docx")) {
            mimeType = "application/vnd.openxmlformats-officedocument.wordprocessingml.document";
        } else {
            throw new IllegalArgumentException("Unsupported file type: " + filename);
        }

        // Prepare Drive file metadata
        File fileMetadata = new File();
        fileMetadata.setName(filename);

        // Use in-memory ByteArrayContent instead of reading from disk
        AbstractInputStreamContent contentStream = new ByteArrayContent(mimeType, fileData);

        Drive driveService = getDriveService();
        // Upload the file to Google Drive
        File uploadedFile = driveService.files()
                .create(fileMetadata, contentStream)
                .setFields("id, name, mimeType, webViewLink")
                .execute();

        System.out.println("File uploaded to Google Drive:");
        System.out.println(" - Name: " + uploadedFile.getName());
        System.out.println(" - ID: " + uploadedFile.getId());
        System.out.println(" - MIME type: " + uploadedFile.getMimeType());
        System.out.println(" - Link: " + uploadedFile.getWebViewLink());

        return uploadedFile;
    }


    public Boolean sendMail(PutMailRequest putMailRequest) throws IOException, GeneralSecurityException, MessagingException {
        // Create the gmail API client
        Gmail service = getGmailService();

        // Create the email content
        String messageSubject = putMailRequest.wasAccepted() ? "Twoje zgłoszenie zostało akceptowane!" : "Twoje zgłoszenie zostało odrzucone.";
        String bodyText = "Witaj kandydacie!\n" +
                "Ministerstwo wojny oraz wielki brat zwracają się dzisiaj do ciebie ze względu na twoją aplikację na pozycję:\n" +
                "   " + putMailRequest.position() + "\n" +
                (putMailRequest.wasAccepted() ? ("Wielki brat docenił twoje starania i twierdzi, że nadajesz się do tej pracy.\n" +
                        "Twoja rozmowa rekrutacyjna została zaplanowana na datę: " + putMailRequest.meetingDetails() +"\n") :
                        ("Ministerstwo wojny jest rozczarowane twoją postawą oraz faktem, że podjąłeś decyzję o aplikowaniu, wiedząc że:\n" +
                                "   " + putMailRequest.Reason() + "\n" +
                                "Twoja egzekucja została zaplanowana na datę: " + putMailRequest.meetingDetails() + "\n")) +
                "Wszyscy w ministerstwie wojny nie możemy doczekać się tego dnia! \n" +
                "Do zobaczenia,\n" +
                "Ministerstwo Wojny";

        // Encode as MIME message
        Properties props = new Properties();
        Session session = Session.getDefaultInstance(props, null);

        MimeMessage email = createEmail(putMailRequest.emailAddress(), "war.ministry.dc25@gmail.com", messageSubject, bodyText, session);

        // Encode and wrap the MIME message into a gmail message
        ByteArrayOutputStream buffer = new ByteArrayOutputStream();
        email.writeTo(buffer);
        byte[] rawMessageBytes = buffer.toByteArray();
        String encodedEmail = Base64.encodeBase64URLSafeString(rawMessageBytes);
        Message message = new Message();
        message.setRaw(encodedEmail);

        try {
            // Create send message
            message = service.users().messages().send("me", message).execute();
            System.out.println("Message id: " + message.getId());
            System.out.println(message.toPrettyString());
            return true;
        } catch (GoogleJsonResponseException e) {
            // TODO handle error appropriately
            GoogleJsonError error = e.getDetails();
            if (error.getCode() == 403) {
                System.err.println("Unable to send message: " + e.getDetails());
            } else {
                throw e;
            }
        }
        return false;
    }

    public Boolean checkIfWasHandled(String id) {
        GmailEntity entity = gmailRepository.findByMessageId(id);
        if (entity != null) {
            return entity.getWasHandled();
        }
        else
        {
            return false;
        }
    }

    private MimeMessage createEmail(String toEmailAddress,
                                          String fromEmailAddress,
                                          String subject,
                                          String bodyText,
                                          Session session)
            throws MessagingException {
        MimeMessage email = new MimeMessage(session);

        email.setFrom(new InternetAddress(fromEmailAddress));
        email.addRecipient(jakarta.mail.Message.RecipientType.TO,
                new InternetAddress(toEmailAddress));
        email.setSubject(subject);
        email.setText(bodyText);
        return email;
    }
}