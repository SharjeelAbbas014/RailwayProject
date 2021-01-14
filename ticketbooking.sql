-- phpMyAdmin SQL Dump
-- version 5.0.4
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Jan 14, 2021 at 04:24 PM
-- Server version: 10.4.17-MariaDB
-- PHP Version: 7.2.34

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `railway`
--

-- --------------------------------------------------------

--
-- Table structure for table `ticketbooking`
--

CREATE TABLE `ticketbooking` (
  `BookID` int(11) NOT NULL,
  `PID` int(11) NOT NULL,
  `ScheduleID` int(11) NOT NULL,
  `Payment` varchar(4) NOT NULL,
  `numoftick` int(11) NOT NULL,
  `dateBought` date NOT NULL DEFAULT current_timestamp(),
  `busOrEco` varchar(2) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Dumping data for table `ticketbooking`
--

INSERT INTO `ticketbooking` (`BookID`, `PID`, `ScheduleID`, `Payment`, `numoftick`, `dateBought`, `busOrEco`) VALUES
(42, 1, 2269, 'Cash', 2, '2021-01-10', 'B'),
(43, 7, 2269, 'Cash', 4, '2021-01-10', 'E'),
(44, 7, 2269, 'Jazz', 2, '2021-01-10', 'E'),
(45, 7, 2271, 'Cash', 2, '2021-01-10', 'B'),
(46, 1, 2269, 'Card', 2, '2021-01-10', 'B'),
(47, 1, 2269, 'Jazz', 2, '2021-01-10', 'B'),
(48, 1, 2269, 'Jazz', 2, '2021-01-10', 'B'),
(49, 1, 2269, 'Jazz', 2, '2021-01-13', 'B'),
(50, 1, 2269, 'Jazz', 2, '2021-01-12', 'E'),
(51, 1, 2277, 'Cash', 3, '2021-01-11', 'B'),
(52, 1, 2261, 'Cash', 2, '2021-01-14', 'E');

--
-- Indexes for dumped tables
--

--
-- Indexes for table `ticketbooking`
--
ALTER TABLE `ticketbooking`
  ADD PRIMARY KEY (`BookID`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `ticketbooking`
--
ALTER TABLE `ticketbooking`
  MODIFY `BookID` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=54;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
