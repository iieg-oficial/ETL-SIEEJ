-- =======================================================================
-- V8: homologar cvegeo_server a placeholders FDW nombrados por la DB real
-- =======================================================================

ALTER SERVER cvegeo_server OPTIONS (
    SET dbname '${fdw_cvegeo_dbname}',
    SET host   '${fdw_cvegeo_host}',
    SET port   '${fdw_cvegeo_port}'
);

ALTER USER MAPPING FOR CURRENT_USER SERVER cvegeo_server OPTIONS (
    SET user     '${fdw_cvegeo_user}',
    SET password '${fdw_cvegeo_password}'
);
