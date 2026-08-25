-- =======================================================================
-- V9: homologar conapo_server a placeholders FDW con sufijo numerico (_2)
-- =======================================================================

ALTER SERVER conapo_server OPTIONS (
    SET dbname '${fdw_dbname_2}',
    SET host   '${fdw_host_2}',
    SET port   '${fdw_port_2}'
);

ALTER USER MAPPING FOR CURRENT_USER SERVER conapo_server OPTIONS (
    SET user     '${fdw_user_2}',
    SET password '${fdw_password_2}'
);
