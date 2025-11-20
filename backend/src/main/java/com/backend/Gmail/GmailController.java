package com.backend.Gmail;

import com.backend.shared.ApplicationMessage;
import com.backend.shared.ApplicationResponseHandler;
import com.backend.shared.EndpointConstants;
import com.google.api.services.gmail.Gmail;
import com.google.api.services.gmail.model.ListLabelsResponse;
import com. google. api. services. gmail. model. Label;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;
import java.util.UUID;

@RestController
@RequestMapping(EndpointConstants.GMAIL)
public class GmailController {

    private final GmailService gmailService;

    public GmailController(GmailService gmailService) {
        this.gmailService = gmailService;
    }

//    @GetMapping("/labels")
//    public List<String> listLabels() throws Exception {
//        Gmail gmail = gmailService.getGmailService();
//        //System.out.println("1");
//        ListLabelsResponse listResponse = gmail.users().labels().list("me").execute();
//        //System.out.println("2");
//        return listResponse.getLabels().stream()
//                .map(Label::getName)
//                .toList();
//    }

    @GetMapping("/inbox/count")
    public int getInboxCount() throws Exception {
        return gmailService.getInboxMessageCount();
    }

    @GetMapping("/inbox/{index}")
    public Map<String, String> getNthNewestMail(@PathVariable int index) throws Exception {
        return gmailService.getNthNewestMail(index);
    }

    @PutMapping("/send")
    public ResponseEntity<String> sendMail(@RequestBody PutMailRequest request) throws Exception {
        boolean success = gmailService.sendMail(request);
        if (success) {
            return ResponseEntity.ok("Email sent successfully.");
        } else {
            return ResponseEntity.status(HttpStatus.FORBIDDEN).body("Failed to send email.");
        }
    }

    public Boolean checkIfWasHandled(int id) {
        return gmailService.checkIfWasHandled(id);
    }
}
