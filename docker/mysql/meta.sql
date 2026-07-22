-- Active: 1783669400084@@localhost@3306@app_meta
-- Active: 1783669400084@@localhost@3306@mysql
-- Meta 数据库（元数据库）用来管理数仓本身的信息
SET NAMES utf8mb4;

CREATE DATABASE IF NOT EXISTS app_meta DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

GRANT All PRIVILEGES ON app_meta.* TO 'yt123456' @'%';

USE app_meta;

DROP TABLE IF EXISTS `table_info`;
CREATE TABLE `table_info` (
    `id` VARCHAR(64) NOT NULL COMMENT '主键',
    `name` VARCHAR(128) NOT NULL COMMENT '物理表名',
    `type` VARCHAR(20) COMMENT '表类型：fact/dimension/bridge',
    `description` VARCHAR(255) COMMENT '该表描述',
    PRIMARY KEY (`id`)
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COMMENT = '数据表元信息';

DROP TABLE IF EXISTS `column_info`;
CREATE TABLE `column_info` (
    `id` VARCHAR(64) NOT NULL COMMENT '主键',
    `table_id` VARCHAR(128) NOT NULL COMMENT '关联meta_tables.id',
    `column_name` VARCHAR(128) NOT NULL COMMENT '物理字段名',
    `type` VARCHAR(50) COMMENT '数据类型：bigint/decimal/varchar/date',
    `description` VARCHAR(128) COMMENT '列描述',
    `alias` JSON COMMENT '别名、同义词',
    `role` VARCHAR(20) DEFAULT 0 COMMENT 'primary_key or dimension',
    `examples` JSON COMMENT '数据示例',
    PRIMARY KEY (`id`)
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COMMENT = '字段元信息';

DROP TABLE IF EXISTS `metric_info`;
CREATE TABLE `metric_info` (
    `id` VARCHAR(64) NOT NULL COMMENT '主键',
    `name` VARCHAR(128) COMMENT '指标名称',
    `description` TEXT COMMENT '指标描述',
    `relevant_columns` JSON COMMENT '关联的列',
    `alias` JSON COMMENT '指标别名',
    PRIMARY KEY (`id`)
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COMMENT = '指标信息表';

DROP TABLE IF EXISTS `column_metric`;
CREATE TABLE `column_metric` (
    `column_id` VARCHAR(64) NOT NULL COMMENT '主键,字段 ID',
    `metric_id` VARCHAR(64) NOT NULL COMMENT '指标 ID',
    PRIMARY KEY (`column_id`)
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COMMENT = '字段与指标关联表';