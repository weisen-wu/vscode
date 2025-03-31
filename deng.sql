/*
 Navicat Premium Dump SQL

 Source Server         : MYSQL
 Source Server Type    : MySQL
 Source Server Version : 80041 (8.0.41)
 Source Host           : localhost:3306
 Source Schema         : deng

 Target Server Type    : MySQL
 Target Server Version : 80041 (8.0.41)
 File Encoding         : 65001

 Date: 24/03/2025 18:31:24
*/

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ----------------------------
-- Table structure for companies
-- ----------------------------
DROP TABLE IF EXISTS `companies`;
CREATE TABLE `companies`  (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `address` varchar(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL,
  `contact_person` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL,
  `phone` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL,
  `email` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL,
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `name`(`name` ASC) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 6 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of companies
-- ----------------------------
INSERT INTO `companies` VALUES (3, 'ST', '', '', '', '');
INSERT INTO `companies` VALUES (4, 'CT', '', '', '', '');
INSERT INTO `companies` VALUES (5, 'SZ', '', '', '', '');

-- ----------------------------
-- Table structure for e_statione
-- ----------------------------
DROP TABLE IF EXISTS `e_statione`;
CREATE TABLE `e_statione`  (
  `id` int NOT NULL AUTO_INCREMENT,
  `mac_id` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `ip_address` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL,
  `location` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL,
  `description` varchar(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL,
  `connection_status` tinyint(1) NULL DEFAULT NULL,
  `last_connected` datetime NULL DEFAULT NULL,
  `created_at` datetime NULL DEFAULT NULL,
  `updated_at` datetime NULL DEFAULT NULL,
  `company_id` int NULL DEFAULT NULL,
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `mac_id`(`mac_id` ASC) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 4 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of e_statione
-- ----------------------------
INSERT INTO `e_statione` VALUES (2, '90A9F7300205', '10.92.87.102', '11', '1', 0, NULL, '2025-03-17 05:26:05', '2025-03-18 08:50:10', 3);
INSERT INTO `e_statione` VALUES (3, 'e3r', '10.92.100.102', '11', '', 0, NULL, '2025-03-17 05:26:25', '2025-03-17 05:26:25', 4);

-- ----------------------------
-- Table structure for light_strip
-- ----------------------------
DROP TABLE IF EXISTS `light_strip`;
CREATE TABLE `light_strip`  (
  `id` int NOT NULL AUTO_INCREMENT,
  `strip_id` varchar(80) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `mac_address` varchar(80) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `work_order` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `last_estatione_mac` varchar(80) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL,
  `operator_name` varchar(80) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `created_at` datetime NULL DEFAULT NULL,
  `updated_at` datetime NULL DEFAULT NULL,
  `company_id` int NULL DEFAULT NULL,
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `strip_id`(`strip_id` ASC) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 35 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of light_strip
-- ----------------------------
INSERT INTO `light_strip` VALUES (8, 'LS20250318152324', 'AD10000416D2', '1', '90A9F7300205', 'a', '2025-03-18 07:23:25', '2025-03-24 03:37:05', 3);
INSERT INTO `light_strip` VALUES (9, 'LS20250318152331', 'AD100003D5FE', '3', '90A9F7300205', 'a', '2025-03-18 07:23:31', '2025-03-19 08:27:41', 3);
INSERT INTO `light_strip` VALUES (16, 'LS20250318163930', 'AD100003C45B', '5', '90A9F7300205', 'a', '2025-03-18 08:39:30', '2025-03-18 09:02:46', 3);
INSERT INTO `light_strip` VALUES (18, 'LS20250318172025', 'AD10000416D3', '6', '', 'a', '2025-03-18 09:20:26', '2025-03-24 03:37:17', 3);

-- ----------------------------
-- Table structure for lightstrip_logs
-- ----------------------------
DROP TABLE IF EXISTS `lightstrip_logs`;
CREATE TABLE `lightstrip_logs`  (
  `id` int NOT NULL AUTO_INCREMENT,
  `operation_type` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `operation_time` datetime NOT NULL,
  `operator_name` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `mac_address` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `work_order` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `details` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL,
  PRIMARY KEY (`id`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 65 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of lightstrip_logs
-- ----------------------------
INSERT INTO `lightstrip_logs` VALUES (1, 'create', '2025-03-17 05:37:23', 'admin', 'AD10000416D2', '1', '新增灯条');
INSERT INTO `lightstrip_logs` VALUES (2, 'delete', '2025-03-17 05:37:26', 'admin', 'AD10000416D2', '1', '删除灯条');
INSERT INTO `lightstrip_logs` VALUES (3, 'create', '2025-03-17 05:37:34', 'a', 'AD10000416D2', '1', '通过APP绑定灯条');
INSERT INTO `lightstrip_logs` VALUES (4, 'create', '2025-03-17 05:37:47', 'a', 'AD100003D5FE', '2', '通过APP绑定灯条');
INSERT INTO `lightstrip_logs` VALUES (5, 'create', '2025-03-17 06:51:42', 'a', '12', '3', '通过APP绑定灯条');
INSERT INTO `lightstrip_logs` VALUES (6, 'create', '2025-03-17 07:30:39', 'a', '4', '4', '通过APP绑定灯条');
INSERT INTO `lightstrip_logs` VALUES (7, 'delete', '2025-03-18 06:40:48', 'a', '4', '4', '通过APP解绑灯条');
INSERT INTO `lightstrip_logs` VALUES (8, 'create', '2025-03-18 06:41:08', 'a', '4', '4', '通过APP绑定灯条');
INSERT INTO `lightstrip_logs` VALUES (9, 'create', '2025-03-18 07:20:41', 'a', '5', '5', '通过APP绑定灯条');
INSERT INTO `lightstrip_logs` VALUES (10, 'delete', '2025-03-18 07:21:41', 'a', '4', '4', '通过APP解绑灯条');
INSERT INTO `lightstrip_logs` VALUES (11, 'delete', '2025-03-18 07:21:46', 'a', '5', '5', '通过APP解绑灯条');
INSERT INTO `lightstrip_logs` VALUES (12, 'delete', '2025-03-18 07:21:52', 'a', '12', '3', '通过APP解绑灯条');
INSERT INTO `lightstrip_logs` VALUES (13, 'delete', '2025-03-18 07:22:12', 'a', 'AD100003D5FE', '2', '通过APP解绑灯条');
INSERT INTO `lightstrip_logs` VALUES (14, 'delete', '2025-03-18 07:22:17', 'a', 'AD10000416D2', '1', '通过APP解绑灯条');
INSERT INTO `lightstrip_logs` VALUES (15, 'create', '2025-03-18 07:23:25', 'a', 'AD10000416D2', '1', '通过APP绑定灯条');
INSERT INTO `lightstrip_logs` VALUES (16, 'create', '2025-03-18 07:23:31', 'a', 'AD100003D5FE', '2', '通过APP绑定灯条');
INSERT INTO `lightstrip_logs` VALUES (17, 'create', '2025-03-18 07:23:34', 'a', '3', '3', '通过APP绑定灯条');
INSERT INTO `lightstrip_logs` VALUES (18, 'create', '2025-03-18 07:28:35', 'a', '4', '4', '通过APP绑定灯条');
INSERT INTO `lightstrip_logs` VALUES (19, 'create', '2025-03-18 07:34:07', 'admin', '5', '5', '新增灯条');
INSERT INTO `lightstrip_logs` VALUES (20, 'delete', '2025-03-18 07:34:23', 'a', '5', '5', '通过APP解绑灯条');
INSERT INTO `lightstrip_logs` VALUES (21, 'create', '2025-03-18 07:34:36', 'admin', '5', '4', '新增灯条');
INSERT INTO `lightstrip_logs` VALUES (22, 'delete', '2025-03-18 07:36:49', 'admin', '5', '4', '删除灯条');
INSERT INTO `lightstrip_logs` VALUES (23, 'create', '2025-03-18 07:41:41', 'a', '5', '4', '通过APP绑定灯条');
INSERT INTO `lightstrip_logs` VALUES (24, 'delete', '2025-03-18 07:42:02', 'a', '4', '4', '通过APP解绑灯条');
INSERT INTO `lightstrip_logs` VALUES (25, 'create', '2025-03-18 08:38:06', 'a', '4', '4', '通过APP绑定灯条');
INSERT INTO `lightstrip_logs` VALUES (26, 'create', '2025-03-18 08:39:30', 'a', 'DT100003C45B', '5', '通过APP绑定灯条');
INSERT INTO `lightstrip_logs` VALUES (27, 'delete', '2025-03-18 09:08:17', 'admin', '5', '4', '删除灯条');
INSERT INTO `lightstrip_logs` VALUES (28, 'create', '2025-03-18 09:19:08', 'a', 'AD110000416D3', '6', '通过APP绑定灯条');
INSERT INTO `lightstrip_logs` VALUES (29, 'delete', '2025-03-18 09:19:33', 'a', 'AD110000416D3', '6', '通过APP解绑灯条');
INSERT INTO `lightstrip_logs` VALUES (30, 'delete', '2025-03-18 09:19:43', 'a', 'AD100003C45A', '4', '通过APP解绑灯条');
INSERT INTO `lightstrip_logs` VALUES (31, 'delete', '2025-03-18 09:19:46', 'a', 'AD100003C45C', '3', '通过APP解绑灯条');
INSERT INTO `lightstrip_logs` VALUES (32, 'create', '2025-03-18 09:20:26', 'a', 'AD10000416D3', '6', '通过APP绑定灯条');
INSERT INTO `lightstrip_logs` VALUES (33, 'create', '2025-03-19 08:49:28', 'a', 'AD17', '7', '通过APP绑定灯条');
INSERT INTO `lightstrip_logs` VALUES (34, 'delete', '2025-03-19 08:49:40', 'a', 'AD17', '7', '通过APP解绑灯条');
INSERT INTO `lightstrip_logs` VALUES (35, 'create', '2025-03-19 08:50:11', 'a', 'AD100003C45H', '7', '通过APP绑定灯条');
INSERT INTO `lightstrip_logs` VALUES (36, 'create', '2025-03-19 09:14:59', 'a', 'AD100002266', '8', '通过APP绑定灯条');
INSERT INTO `lightstrip_logs` VALUES (37, 'delete', '2025-03-19 09:19:18', 'a', 'AD100003C45H', '7', '通过APP解绑灯条');
INSERT INTO `lightstrip_logs` VALUES (38, 'delete', '2025-03-19 09:19:18', 'a', 'AD100002266', '8', '通过APP解绑灯条');
INSERT INTO `lightstrip_logs` VALUES (39, 'create', '2025-03-20 01:08:00', 'a', 'AD17777777', '7', '通过APP绑定灯条');
INSERT INTO `lightstrip_logs` VALUES (40, 'create', '2025-03-20 01:08:05', 'a', 'AD188888888', '8', '通过APP绑定灯条');
INSERT INTO `lightstrip_logs` VALUES (41, 'delete', '2025-03-20 01:10:49', 'a', 'AD10000416D7', '7', '通过APP解绑灯条');
INSERT INTO `lightstrip_logs` VALUES (42, 'delete', '2025-03-20 01:10:49', 'a', 'AD10000416D8', '8', '通过APP解绑灯条');
INSERT INTO `lightstrip_logs` VALUES (43, 'create', '2025-03-20 01:13:50', 'a', 'AD10000416D7', '7', '通过APP绑定灯条');
INSERT INTO `lightstrip_logs` VALUES (44, 'create', '2025-03-20 01:13:59', 'a', 'AD10000416D8', '8', '通过APP绑定灯条');
INSERT INTO `lightstrip_logs` VALUES (45, 'delete', '2025-03-20 01:14:11', 'a', 'AD10000416D7', '7', '通过APP解绑灯条');
INSERT INTO `lightstrip_logs` VALUES (46, 'delete', '2025-03-20 01:14:11', 'a', 'AD10000416D8', '8', '通过APP解绑灯条');
INSERT INTO `lightstrip_logs` VALUES (47, 'create', '2025-03-20 01:15:56', 'admin', 'AD10000416D7', '7', '新增灯条');
INSERT INTO `lightstrip_logs` VALUES (48, 'create', '2025-03-20 01:16:04', 'admin', 'AD10000416D8', '8', '新增灯条');
INSERT INTO `lightstrip_logs` VALUES (49, 'delete', '2025-03-20 01:17:47', 'a', 'AD10000416D7', '7', '通过APP解绑灯条');
INSERT INTO `lightstrip_logs` VALUES (50, 'delete', '2025-03-20 01:17:47', 'a', 'AD10000416D8', '8', '通过APP解绑灯条');
INSERT INTO `lightstrip_logs` VALUES (51, 'create', '2025-03-20 02:07:28', 'a', 'AD10000416D7', '7', '通过APP绑定灯条');
INSERT INTO `lightstrip_logs` VALUES (52, 'create', '2025-03-20 02:07:34', 'a', 'AD10000416D8', '8', '通过APP绑定灯条');
INSERT INTO `lightstrip_logs` VALUES (53, 'delete', '2025-03-20 02:17:48', 'a', 'AD10000416D7', '7', '通过APP解绑灯条');
INSERT INTO `lightstrip_logs` VALUES (54, 'delete', '2025-03-20 02:17:48', 'a', 'AD10000416D8', '8', '通过APP解绑灯条');
INSERT INTO `lightstrip_logs` VALUES (55, 'create', '2025-03-20 02:18:25', 'a', 'AD10000416D7', '7', '通过APP绑定灯条');
INSERT INTO `lightstrip_logs` VALUES (56, 'create', '2025-03-20 02:18:31', 'a', 'AD10000416D8', '8', '通过APP绑定灯条');
INSERT INTO `lightstrip_logs` VALUES (57, 'delete', '2025-03-20 02:20:48', 'a', 'AD10000416D7', '7', '通过APP解绑灯条');
INSERT INTO `lightstrip_logs` VALUES (58, 'delete', '2025-03-20 02:20:48', 'a', 'AD10000416D8', '8', '通过APP解绑灯条');
INSERT INTO `lightstrip_logs` VALUES (59, 'create', '2025-03-20 03:55:29', 'a', 'AD10000416D7', '7', '通过APP绑定灯条');
INSERT INTO `lightstrip_logs` VALUES (60, 'delete', '2025-03-20 04:05:46', 'a', 'AD10000416D7', '7', '通过APP解绑灯条');
INSERT INTO `lightstrip_logs` VALUES (61, 'create', '2025-03-21 09:00:55', 'a', 'AD19', '9', '通过APP绑定灯条');
INSERT INTO `lightstrip_logs` VALUES (62, 'delete', '2025-03-21 09:01:02', 'a', 'AD19', '9', '通过APP解绑灯条');
INSERT INTO `lightstrip_logs` VALUES (63, 'create', '2025-03-21 09:09:50', 'a', 'AD19', '9', '通过APP绑定灯条');
INSERT INTO `lightstrip_logs` VALUES (64, 'delete', '2025-03-21 09:09:57', 'a', 'AD19', '9', '通过APP解绑灯条');

-- ----------------------------
-- Table structure for system_config
-- ----------------------------
DROP TABLE IF EXISTS `system_config`;
CREATE TABLE `system_config`  (
  `id` int NOT NULL AUTO_INCREMENT,
  `check_lightstrip_duplicate` tinyint(1) NOT NULL,
  PRIMARY KEY (`id`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 2 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of system_config
-- ----------------------------
INSERT INTO `system_config` VALUES (1, 0);

-- ----------------------------
-- Table structure for test_po
-- ----------------------------
DROP TABLE IF EXISTS `test_po`;
CREATE TABLE `test_po`  (
  `id` int NOT NULL,
  `po_order` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL,
  `work_order` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL,
  `work_ph` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL,
  `work_pm` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL,
  `work_sl` int NULL DEFAULT NULL,
  PRIMARY KEY (`id`) USING BTREE
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of test_po
-- ----------------------------
INSERT INTO `test_po` VALUES (1, 'a', '1', 'JJ7.0-103AFB1-01D-CY1\r\n', '限位片\r\n', 22);
INSERT INTO `test_po` VALUES (2, 'a', '2', 'JJ7.0-103AFB1-01D-CY2\r\n', '装饰环\r\n', 10);
INSERT INTO `test_po` VALUES (3, 'a', '3', 'JJ7.0-122-05A-CY1\r\n', '灯箱主体\r\n', 5);
INSERT INTO `test_po` VALUES (4, 'a', '4', 'JJ7.0-122-05A-CY2\r\n', 'L型封口片\r\n', 6);
INSERT INTO `test_po` VALUES (5, 'b', '5', 'JJ7.0-209B-01-WJ1\r\n', '中间连接片\r\n', 9);
INSERT INTO `test_po` VALUES (6, 'b', '6', 'JJ7.0-209B-01-WJ2\r\n', '竖杆B\r\n', 8);
INSERT INTO `test_po` VALUES (7, 'c', '7', '12112', '232', 2);
INSERT INTO `test_po` VALUES (8, 'c', '8', NULL, NULL, NULL);

-- ----------------------------
-- Table structure for user
-- ----------------------------
DROP TABLE IF EXISTS `user`;
CREATE TABLE `user`  (
  `id` int NOT NULL AUTO_INCREMENT,
  `username` varchar(80) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `password_hash` varchar(128) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL,
  `department` varchar(80) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `is_admin` tinyint(1) NULL DEFAULT NULL,
  `created_at` datetime NULL DEFAULT NULL,
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `username`(`username` ASC) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 2 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of user
-- ----------------------------
INSERT INTO `user` VALUES (1, 'admin', 'pbkdf2:sha256:600000$rWMGwHtURhR5RAam$a8a8c28fc2004c12c1c7e156cde5b4c727a5a28864b61b01a86ec84da144e317', '管理部', 1, '2025-03-17 02:43:48');

-- ----------------------------
-- Table structure for users
-- ----------------------------
DROP TABLE IF EXISTS `users`;
CREATE TABLE `users`  (
  `id` int NOT NULL AUTO_INCREMENT,
  `username` varchar(80) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `department` varchar(120) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `password_hash` varchar(128) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL,
  `company_id` int NULL DEFAULT NULL,
  `colors` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL,
  `time` int NULL DEFAULT NULL,
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `username`(`username` ASC) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 4 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of users
-- ----------------------------
INSERT INTO `users` VALUES (1, 'a', 'a', 'pbkdf2:sha256:600000$uYHUzJq0TSSUAOvL$2b29122df268308cc89e63fa7cc9080856300f5b77a73ac85748f75337645f85', 3, 'red', 1);
INSERT INTO `users` VALUES (3, 'b', 'b', 'pbkdf2:sha256:600000$vMau4NUnGWLIRksh$fb0dbe71bb8acc6cb87ac7465f13d1e72991903c03978682a641d2fddbdca1c7', 3, 'blue', 2);

SET FOREIGN_KEY_CHECKS = 1;
