package com.backend.Gmail;

import com.google.api.client.auth.oauth2.Credential;
import com.google.api.client.extensions.java6.auth.oauth2.AuthorizationCodeInstalledApp;
import com.google.api.client.extensions.jetty.auth.oauth2.LocalServerReceiver;
import com.google.api.client.googleapis.auth.oauth2.GoogleAuthorizationCodeFlow;
import com.google.api.client.googleapis.auth.oauth2.GoogleClientSecrets;
import com.google.api.client.googleapis.javanet.GoogleNetHttpTransport;
import com.google.api.client.googleapis.json.GoogleJsonError;
import com.google.api.client.googleapis.json.GoogleJsonResponseException;
import com.google.api.client.http.HttpRequestInitializer;
import com.google.api.client.http.javanet.NetHttpTransport;
import com.google.api.client.json.JsonFactory;
import com.google.api.client.json.gson.GsonFactory;
import com.google.api.client.util.store.FileDataStoreFactory;
import com.google.api.services.gmail.Gmail;
import com.google.api.services.gmail.GmailScopes;
import com.google.api.services.gmail.model.ListMessagesResponse;
import com.google.api.services.gmail.model.Message;
import com.google.api.services.gmail.model.MessagePart;
import com.google.api.services.gmail.model.MessagePartHeader;
import com.google.auth.http.HttpCredentialsAdapter;
import org.apache.commons.codec.binary.Base64;
import org.springframework.stereotype.Service;
import com.google.auth.oauth2.GoogleCredentials;

import jakarta.mail.*;
import jakarta.mail.internet.*;

import java.io.*;
import java.security.GeneralSecurityException;
import java.util.List;
import java.util.Map;
import java.util.Properties;

@Service
public class GmailService {
    private static final String APPLICATION_NAME = "DokumentyCyfrowe25";
    private static final JsonFactory JSON_FACTORY = GsonFactory.getDefaultInstance();
    private static final String TOKENS_DIRECTORY_PATH = "./tokens";

    private static final List<String> SCOPES = List.of(GmailScopes.GMAIL_READONLY, GmailScopes.GMAIL_LABELS, GmailScopes.GMAIL_COMPOSE, GmailScopes.GMAIL_SEND, GmailScopes.GMAIL_MODIFY);
    private static final String CREDENTIALS_FILE_PATH = "/client_secret_270311492495-ip027ghqo1181v4qd288vv2203rjnu5v.apps.googleusercontent.com.json";

    public Gmail getService() throws IOException, GeneralSecurityException {
        final NetHttpTransport httpTransport = GoogleNetHttpTransport.newTrustedTransport();
        Credential credential = getCredentials(httpTransport);
        return new Gmail.Builder(httpTransport, JSON_FACTORY, credential)
                .setApplicationName(APPLICATION_NAME)
                .build();
    }

    private Credential getCredentials(final com.google.api.client.http.javanet.NetHttpTransport httpTransport)
            throws IOException {
        InputStream in = getClass().getResourceAsStream(CREDENTIALS_FILE_PATH);
        if (in == null) {
            throw new FileNotFoundException("Resource not found: " + CREDENTIALS_FILE_PATH);
        }
        GoogleClientSecrets clientSecrets =
                GoogleClientSecrets.load(JSON_FACTORY, new InputStreamReader(in));

        GoogleAuthorizationCodeFlow flow = new GoogleAuthorizationCodeFlow.Builder(
                httpTransport, JSON_FACTORY, clientSecrets, SCOPES)
                .setDataStoreFactory(new FileDataStoreFactory(new File(TOKENS_DIRECTORY_PATH)))
                .setAccessType("offline")
                .build();

        var receiver = new com.google.api.client.extensions.jetty.auth.oauth2.LocalServerReceiver.Builder()
                .setPort(8888)
                .build();

        return new com.google.api.client.extensions.java6.auth.oauth2.AuthorizationCodeInstalledApp(flow, receiver)
                .authorize("user");
    }

    public int getInboxMessageCount() throws IOException, GeneralSecurityException {
        Gmail service = getService();
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

    public Map<String, String> getNthNewestMail(int index) throws IOException, GeneralSecurityException {
        Gmail service = getService();

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
        Message message = service.users().messages().get("me", messageId).setFormat("full").execute();

        // Extract basic info
        MessagePart payload = message.getPayload();
        List<MessagePartHeader> headers = payload.getHeaders();
        String subject = getHeader(headers, "Subject");
        String from = getHeader(headers, "From");
        String date = getHeader(headers, "Date");

        String snippet = message.getSnippet();

        return Map.of(
                "id", messageId,
                "from", from,
                "subject", subject,
                "date", date,
                "snippet", snippet
        );
    }

    private String getHeader(List<MessagePartHeader> headers, String name) {
        return headers.stream()
                .filter(h -> h.getName().equalsIgnoreCase(name))
                .map(MessagePartHeader::getValue)
                .findFirst()
                .orElse("(unknown)");
    }

    public Boolean sendMail(PutMailRequest putMailRequest) throws IOException, GeneralSecurityException, MessagingException {
        // Create the gmail API client
        Gmail service = getService();

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