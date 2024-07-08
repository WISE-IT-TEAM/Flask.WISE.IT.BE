CREATE TABLE `Artist` (
  `id` integer PRIMARY KEY,
  `group_name` text,
  `agency` text,
  `debut_date` date
);

CREATE TABLE `Member` (
  `id` integer PRIMARY KEY,
  `member_name` text,
  `gender` text,
  `birthday` date,
  `country` text,
  `artist_id` integer,
  FOREIGN KEY (artist_id) REFERENCES Artist(id)
);

CREATE TABLE `Album` (
  `id` integer PRIMARY KEY,
  `album_name` text,
  `release_date` date,
  `album_type` text,
  `sales_volume` float,
  `artist_id` integer,
  FOREIGN KEY (artist_id) REFERENCES Artist(id)
);

CREATE TABLE `Track` (
  `id` integer PRIMARY KEY,
  `title` text,
  `streaming_count` integer,
  `album_id` integer,
  FOREIGN KEY (album_id) REFERENCES Album(id)
);
