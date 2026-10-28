-- Inert additional provisioning source for one fresh disposable cluster only.
-- Run, if separately admitted, beside the existing four-role provision source.
-- No LOGIN, credential, existing-role alteration, membership or default grant.
CREATE ROLE raisa_local_invitation_functions NOLOGIN NOSUPERUSER NOBYPASSRLS
    NOINHERIT NOCREATEROLE NOCREATEDB NOREPLICATION;
