package com.backend.Gmail;

import com.backend.shared.EndpointConstants;
import com.google.api.services.gmail.Gmail;
import com.google.api.services.gmail.model.ListLabelsResponse;
import com. google. api. services. gmail. model. Label;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.List;
import java.util.Map;

@RestController
@RequestMapping(EndpointConstants.GMAIL)
public class GmailController {

    private final GmailService gmailService;

    public GmailController(GmailService gmailService) {
        this.gmailService = gmailService;
    }

    @GetMapping("/labels")
    public List<String> listLabels() throws Exception {
        Gmail gmail = gmailService.getService();
        System.out.println("1");
        ListLabelsResponse listResponse = gmail.users().labels().list("me").execute();
        System.out.println("2");
        return listResponse.getLabels().stream()
                .map(Label::getName)
                .toList();
    }

    @GetMapping("/inbox/count")
    public int getInboxCount() throws Exception {
        return gmailService.getInboxMessageCount();
    }

    @GetMapping("/inbox/{index}")
    public Map<String, String> getNthNewestMail(@PathVariable int index) throws Exception {
        return gmailService.getNthNewestMail(index);
    }
}
