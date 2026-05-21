---
title: CRM Terms of Service (Draft)
status: draft
spec-id: crm.terms-of-service
version: 1.0-draft
effective_date: TBD
---

# Terms of Service: CRM Application

**Version**: 1.0-draft  
**Last Updated**: 2026-05-18  
**Status**: For Legal + Product Review

> **Note**: This is a draft template based on ADR-201 (GDPR deletion strategy) and the CRM PRD. Sections marked **[DRAFT]** require Legal review and approval before publication.

## Data Deletion and Right to Erasure

**[DRAFT: This section is based on ADR-201 and must be reviewed by Legal before publication.]**

### Your Right to Request Deletion

In compliance with GDPR Article 17 (Right to Erasure) and similar data protection laws, you may request that we delete any contact record or associated data from our system at any time. To request deletion, you may:
- Use the "Delete" function in the contact record interface, or
- Contact our support team at support@[domain] with the contact name and record ID

### What Happens When You Delete a Record

When you request deletion:
1. **Immediate Soft Deletion**: The contact record and all linked activities, opportunities, and notes are immediately hidden from your team's view and cannot be accessed through normal search or reporting functions.
2. **Grace Period**: You have 90 days from the deletion date to restore the record if deletion was made in error. During this grace period, you may contact our support team to request restoration.
3. **Permanent Deletion**: After 90 days, the record is permanently deleted from our system and cannot be recovered.

### What Data Is Deleted

Deletion applies to:
- Contact name, email, phone number, title, and company
- All activities (calls, emails, meetings) linked to the contact
- All opportunities and leads associated with the contact
- Contact history and notes

We retain deletion event logs (timestamp, user who requested deletion, and confirmation of deletion) indefinitely for compliance and fraud prevention purposes.

### What Data Is NOT Deleted

The following data is retained for legal and compliance reasons:
- Audit logs of the deletion request itself (for GDPR compliance proof)
- Financial transaction records and contract history (if applicable, per 7-year legal hold)
- Backup copies held for disaster recovery (deleted within standard backup retention window of 30 days)

### Proof of Deletion

Upon deletion, you will receive an email confirmation with:
- Deletion timestamp and transaction ID
- Grace period expiration date (90 days from deletion)
- Link to download deletion audit report for your records

You may request a formal deletion certificate from our support team at any time for compliance documentation.

### Data Export Before Deletion

Before deleting a contact, you may export all associated data (CRM activity history, notes, communications) in CSV format to retain a personal copy. Use the "Export Records" function in the CRM or contact support for bulk export.

### Questions?

For questions about data deletion, privacy, or your rights under GDPR and similar laws, please contact our Privacy Team at privacy@[domain].

---

## Additional Sections [PLACEHOLDER]

The following sections are required for a complete Terms of Service but are outside the scope of ADR-201 and should be drafted separately:

- **Use of Service**: Permitted uses, restrictions, prohibited activities
- **User Accounts and Credentials**: Account creation, security responsibilities, password management
- **Intellectual Property**: Ownership of data, customer data rights, our IP
- **Limitation of Liability**: Disclaimers, liability caps
- **Indemnification**: Customer indemnification obligations
- **Confidentiality**: NDA and confidential information handling
- **Term and Termination**: Service period, termination rights, data after termination
- **Dispute Resolution**: Governing law, arbitration, jurisdiction
- **Modifications to Terms**: How we notify changes to ToS
- **Contact Information**: Legal contact details, privacy inquiries

---

## References

- **ADR-201**: GDPR Data Deletion & Right-to-Forget Implementation Strategy
- **CRM PRD**: Product requirements including GDPR compliance (R-8)
- **GDPR Article 17**: Right to Erasure
- **GDPR Article 20**: Data Portability

---

**Next Steps**:
1. Legal review of "Data Deletion and Right to Erasure" section
2. Draft remaining ToS sections
3. Product sign-off on language and grace period details
4. Public-facing version publication upon service launch
