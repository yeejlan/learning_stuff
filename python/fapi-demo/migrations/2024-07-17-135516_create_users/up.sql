--
-- 表的结构 `users`
--

CREATE TABLE `users` (
  `id` bigint(20) NOT NULL,
  `name` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `email` varchar(50) CHARACTER SET ascii DEFAULT NULL,
  `password` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `status` int(11) DEFAULT '1',
  `note` varchar(1000) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT NULL,
  `updated_at` timestamp NULL DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- 转存表中的数据 `users`
--

INSERT INTO `users` (`id`, `name`, `email`, `password`, `status`, `note`, `created_at`, `updated_at`) VALUES
(1, '中文名测试', 'yee@163.com', '121113+232', 2, NULL, '2023-07-18 14:05:07', NULL),
(4, 'lan', 'lan@163.com', '121113+232', 1, NULL, '2023-07-18 14:05:07', NULL),
(5, '卡卡', 'kaka@163.com', '121113+232', 1, NULL, '2023-07-18 14:05:07', NULL),
(6, '書か', 'kaka2@163.com', '121113+232', 3, NULL, '2023-07-18 14:05:07', NULL),
(7, 'n123', 'n123@aa.com', 'mypass 123', 1, NULL, '2023-08-18 06:04:17', '2023-08-18 06:04:17'),
(9, '宋喀', 'sska@cc.88', '821sasaad', 1, NULL, '2023-08-18 06:23:30', '2023-08-18 06:23:30'),
(10, '吕莹', 'lvying@cc.88', '821sasa1ad', 1, NULL, '2023-08-18 06:30:11', '2023-08-18 06:30:11'),
(11, '小宝', 'bao@cc.88', '821sasa1ad', 2, NULL, '2023-08-18 06:34:51', '2023-08-18 06:34:51'),
(13, 'candara', 'candara@cc.88', '821sasa1ad', 1, NULL, '2023-08-18 06:46:20', '2023-08-18 06:46:20'),
(14, '鹿のこのこのこ', 'dddd@dd.com', 'can not see me', 1, NULL, '2024-07-16 21:34:12', '2024-07-16 21:34:12');

--
-- 转储表的索引
--

--
-- 表的索引 `users`
--
ALTER TABLE `users`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `users_email_unique` (`email`);

--
-- 在导出的表使用AUTO_INCREMENT
--

--
-- 使用表AUTO_INCREMENT `users`
--
ALTER TABLE `users`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=15;
COMMIT;