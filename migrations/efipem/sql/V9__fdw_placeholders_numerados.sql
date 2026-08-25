-- =======================================================================
-- V9: homologar conapo_server e inpc_server a placeholders FDW con
-- sufijo numerico (_2 para conapo, _3 para inpc)
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

ALTER SERVER inpc_server OPTIONS (
    SET dbname '${fdw_dbname_3}',
    SET host   '${fdw_host_3}',
    SET port   '${fdw_port_3}'
);

ALTER USER MAPPING FOR CURRENT_USER SERVER inpc_server OPTIONS (
    SET user     '${fdw_user_3}',
    SET password '${fdw_password_3}'
);
