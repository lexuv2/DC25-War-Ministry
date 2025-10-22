package com.backend.Gmail;

import com.google.api.client.auth.oauth2.Credential;
import com.google.api.client.extensions.java6.auth.oauth2.AuthorizationCodeInstalledApp;
import com.google.api.client.extensions.jetty.auth.oauth2.LocalServerReceiver;
import com.google.api.client.googleapis.auth.oauth2.GoogleAuthorizationCodeFlow;
import com.google.api.client.googleapis.auth.oauth2.GoogleClientSecrets;
import com.google.api.client.googleapis.javanet.GoogleNetHttpTransport;
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
import org.springframework.stereotype.Service;

import java.io.*;
import java.security.GeneralSecurityException;
import java.util.List;
import java.util.Map;

@Service
public class GmailService {
    private static final String APPLICATION_NAME = "DokumentyCyfrowe25";
    private static final JsonFactory JSON_FACTORY = GsonFactory.getDefaultInstance();
    private static final String TOKENS_DIRECTORY_PATH = "/tokens";

    private static final List<String> SCOPES = List.of(GmailScopes.GMAIL_READONLY, GmailScopes.GMAIL_LABELS, GmailScopes.GMAIL_COMPOSE, GmailScopes.GMAIL_SEND);
    private static final String CREDENTIALS_FILE_PATH = "/client_secret_270311492495-dgnlva6ccn765s5llu4g8ea9ulksk534.apps.googleusercontent.com.json";

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


}