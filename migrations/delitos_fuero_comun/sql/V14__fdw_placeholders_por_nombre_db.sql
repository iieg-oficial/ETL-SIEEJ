-- =======================================================================
-- V14: homologar conapo_server a placeholders FDW nombrados por la DB real
-- Retira el placeholder ad-hoc fdw_conapo_port (solo cubria el puerto) y lo
-- reemplaza por el bloque estandar completo de 5 keys fdw_conapo_*
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
