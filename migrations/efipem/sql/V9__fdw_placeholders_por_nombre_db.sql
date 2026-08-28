-- =======================================================================
-- V9: homologar conapo_server e inpc_server a placeholders FDW nombrados
-- por la DB real (fdw_conapo_*, fdw_inpc_*)
-- =======================================================================

ALTER SERVER conapo_server OPTIONS (
    SET dbname '${fdw_conapo_dbname}',
    SET host   '${fdw_conapo_host}',
    SET port   '${fdw_conapo_port}'
);

ALTER USER MAPPING FOR CURRENT_USER SERVER conapo_server OPTIONS (
    SET user     '${fdw_conapo_user}',
    SET password '${fdw_conapo_password}'
);

ALTER SERVER inpc_server OPTIONS (
    SET dbname '${fdw_inpc_dbname}',
    SET host   '${fdw_inpc_host}',
    SET port   '${fdw_inpc_port}'
);

ALTER USER MAPPING FOR CURRENT_USER SERVER inpc_server OPTIONS (
    SET user     '${fdw_inpc_user}',
    SET password '${fdw_inpc_password}'
);
