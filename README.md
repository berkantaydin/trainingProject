STEPS
===============================================

./manage syncdb

===============================================

ALTER TABLE public.auth_user
 ADD CONSTRAINT unique_email UNIQUE (email);

===============================================