package com.backend.Gmail;


import org.springframework.data.jpa.repository.JpaRepository;

import java.util.UUID;

public interface GmailRepository extends JpaRepository<GmailEntity, UUID> {
    GmailEntity findByMessageId(int messageId);
}
