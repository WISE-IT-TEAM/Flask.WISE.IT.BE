-- ? SELECT *
-- 모든 아티스트의 정보를 조회합니다.
SELECT * FROM Artist;

-- 모든 앨범의 정보를 조회합니다.
SELECT * FROM Album;


-- ? SELECT specific columns
-- 아티스트의 그룹 이름과 소속사만 조회합니다.
SELECT group_name, agency FROM Artist;

-- 멤버의 이름과 포지션만 조회합니다.
SELECT member_name, position FROM Member;


-- ? WHERE ... Equals
-- 'SM' 소속 아티스트를 조회합니다.
SELECT * FROM Artist WHERE agency = 'SM';

-- '메인보컬' 포지션의 멤버를 조회합니다.
SELECT * FROM Member WHERE position = '메인보컬';


-- ? WHERE ... Greater than
-- 판매량이 100만장을 넘는 앨범을 조회합니다.
SELECT * FROM Album WHERE sales_volume > 1000000;

-- 2000년 이후 출생한 멤버를 조회합니다.
SELECT * FROM Member WHERE birthday > '2000-01-01';


-- ? WHERE ... Greater than or equal
-- 2020년 1월 1일 이후 데뷔한 아티스트를 조회합니다.
SELECT * FROM Artist WHERE debut_date >= '2020-01-01';

-- 판매량이 50만장 이상인 앨범을 조회합니다.
SELECT * FROM Album WHERE sales_volume >= 500000;


-- ? AND
-- 한국 출신의 남성 멤버를 조회합니다.
SELECT * FROM Member WHERE gender = '남' AND country = '한국';

-- 2022년에 발매된 정규앨범을 조회합니다.
SELECT * FROM Album WHERE album_type = '정규' AND YEAR(release_date) = 2022;


-- ? OR
-- 'SM'이나 'JYP' 소속 아티스트를 조회합니다.
SELECT * FROM Artist WHERE agency = 'SM' OR agency = '';

-- '메인보컬'이나 '메인래퍼' 포지션의 멤버를 조회합니다.
SELECT * FROM Member WHERE position = '메인보컬' OR position = '메인래퍼';


-- ? IN
-- 앨범 타입이 '정규', '미니' 중 하나인 앨범을 조회합니다.
SELECT * FROM Album WHERE album_type IN ('정규', '미니');

-- 일본, 중국 출신 멤버를 조회합니다.
SELECT * FROM Member WHERE country IN ('일본', '중국');


-- ? DISTINCT
-- 중복을 제거한 소속사 목록을 조회합니다.
SELECT DISTINCT agency FROM Artist;

-- 중복을 제거한 앨범 타입 목록을 조회합니다.
SELECT DISTINCT album_type FROM Album;


-- ? ORDER BY
-- 앨범을 발매일 기준 내림차순으로 정렬하여 조회합니다.
SELECT * FROM Album ORDER BY release_date DESC;

-- 멤버를 생일 기준 오름차순으로 정렬하여 조회합니다.
SELECT * FROM Member ORDER BY birthday ASC;


-- ? LIMIT # of returned rows
-- 가장 최근에 데뷔한 5개 아티스트를 조회합니다.
SELECT * FROM Artist ORDER BY debut_date DESC LIMIT 5;

-- 판매량 기준 상위 10개 앨범을 조회합니다.
SELECT * FROM Album ORDER BY sales_volume DESC LIMIT 10;


-- ? COUNT(*)
-- 전체 멤버 수를 조회합니다.
SELECT COUNT(*) FROM Member;

-- 전체 앨범 수를 조회합니다.
SELECT COUNT(*) FROM Album;


-- ? COUNT(*) ... WHERE
-- 정규 앨범의 개수를 조회합니다.
SELECT COUNT(*) FROM Album WHERE album_type = '정규';

-- 여성 멤버의 수를 조회합니다.
SELECT COUNT(*) FROM Member WHERE gender = '여';


-- ? SUM
-- 모든 앨범의 총 판매량을 조회합니다.
SELECT SUM(sales_volume) FROM Album;

-- 특정 아티스트(ID:1)의 총 앨범 판매량을 조회합니다.
SELECT SUM(sales_volume) FROM Album WHERE artist_id = 1;


-- ? AVG
-- 전체 앨범의 평균 판매량을 조회합니다.
SELECT AVG(sales_volume) FROM Album;

-- 정규 앨범의 평균 판매량을 조회합니다.
SELECT AVG(sales_volume) FROM Album WHERE album_type = '정규';


-- ? MAX and MIN
-- 가장 많이 팔린 앨범과 가장 적게 팔린 앨범의 판매량을 조회합니다.
SELECT MAX(sales_volume), MIN(sales_volume) FROM Album;

-- 가장 나이가 많은 멤버와 가장 어린 멤버의 생일을 조회합니다.
SELECT MAX(birthday), MIN(birthday) FROM Member;


-- ? GROUP BY
-- 아티스트 별 앨범 수를 조회합니다.
SELECT artist_id, COUNT(*) FROM Album GROUP BY artist_id;

-- 국가 별 멤버 수를 조회합니다.
SELECT country, COUNT(*) FROM Member GROUP BY country;


-- ? Nested queries
-- 100만장 이상 판매된 앨범이 있는 아티스트를 조회합니다.
SELECT * FROM Artist WHERE id IN (SELECT artist_id FROM Album WHERE sales_volume > 1000000);

-- 가장 많은 앨범을 발매한 아티스트의 정보를 조회합니다.
SELECT * FROM Artist WHERE id = (
    SELECT artist_id 
    FROM Album 
    GROUP BY artist_id 
    ORDER BY COUNT(*) DESC 
    LIMIT 1
);


-- ? NULL
-- 포지션이 지정되지 않은 멤버를 조회합니다.
SELECT * FROM Member WHERE position IS NULL;

-- 판매량 데이터가 없는 앨범을 조회합니다.
SELECT * FROM Album WHERE sales_volume IS NULL;


-- ? Date
-- 2022년에 데뷔한 아티스트를 조회합니다.
SELECT * FROM Artist WHERE strftime('%Y', debut_date) = '2022';

-- 2023년 상반기(1월~6월)에 발매된 앨범을 조회합니다.
SELECT * FROM Album WHERE release_date BETWEEN '2023-01-01' AND '2023-06-30';


-- ? Inner joins
-- 각 아티스트의 앨범 목록을 조회합니다.
SELECT Artist.group_name, Album.album_name 
FROM Artist 
INNER JOIN Album ON Artist.id = Album.artist_id;

-- 각 멤버의 소속 그룹을 조회합니다.
SELECT Member.member_name, Artist.group_name 
FROM Member 
INNER JOIN Artist ON Member.artist_id = Artist.id;


-- -- ? Multiple joins
-- -- 각 아티스트의 멤버와 앨범 정보를 함께 조회합니다.
-- SELECT Artist.group_name, Member.member_name, Album.album_name
-- FROM Artist 
-- INNER JOIN Member ON Artist.id = Member.artist_id
-- INNER JOIN Album ON Artist.id = Album.artist_id;

-- -- 각 앨범의 아티스트와 멤버 정보를 함께 조회합니다.
-- SELECT Album.album_name, Artist.group_name, Member.member_name
-- FROM Album
-- INNER JOIN Artist ON Album.artist_id = Artist.id
-- INNER JOIN Member ON Artist.id = Member.artist_id;


-- ? Joins with WHERE
-- 200만장 이상 판매된 앨범과 해당 아티스트 정보를 조회합니다.
SELECT Artist.group_name, Album.album_name, Album.sales_volume
FROM Artist
INNER JOIN Album ON Artist.id = Album.artist_id
WHERE Album.sales_volume > 2000000;

-- 중국 출신 멤버가 있는 그룹의 정보를 조회합니다. *이중국적의 경우 나오지 않음. LIKE 페이지를 참조하기
SELECT DISTINCT Artist.group_name, Artist.agency
FROM Artist
INNER JOIN Member ON Artist.id = Member.artist_id
WHERE Member.country = '중국';


-- -- ? Left joins
-- -- 모든 아티스트와 그들의 앨범 정보를 조회합니다. 앨범이 없는 아티스트도 포함됩니다.
-- SELECT Artist.group_name, Album.album_name
-- FROM Artist
-- LEFT JOIN Album ON Artist.id = Album.artist_id;

-- -- 모든 멤버와 그들의 소속 그룹 정보를 조회합니다. 그룹에 속하지 않은 멤버도 포함됩니다.
-- SELECT Member.member_name, Artist.group_name
-- FROM Member
-- LEFT JOIN Artist ON Member.artist_id = Artist.id;


-- ? Table alias
-- 테이블 별칭을 사용하여 각 아티스트의 앨범 정보를 조회합니다.
SELECT a.group_name, al.album_name
FROM Artist a
INNER JOIN Album al ON a.id = al.artist_id;

-- 테이블 별칭을 사용하여 각 멤버의 소속 그룹과 데뷔일을 조회합니다.
SELECT m.member_name, a.group_name, a.debut_date
FROM Member m
INNER JOIN Artist a ON m.artist_id = a.id;


-- ? Column alias
-- 컬럼 별칭을 사용하여 아티스트 정보를 조회합니다.
SELECT group_name AS "그룹명", agency AS "소속사", debut_date AS "데뷔일"
FROM Artist;

-- 컬럼 별칭을 사용하여 앨범 판매량 통계를 조회합니다.
SELECT 
    AVG(sales_volume) AS average_sales,
    MAX(sales_volume) AS best_selling,
    MIN(sales_volume) AS least_selling
FROM Album;


-- -- ? Self joins
-- -- 같은 소속사의 다른 그룹 쌍을 조회합니다.
-- SELECT a1.group_name AS group1, a2.group_name AS group2, a1.agency
-- FROM Artist a1
-- JOIN Artist a2 ON a1.agency = a2.agency AND a1.id < a2.id;

-- -- 같은 국가 출신의 다른 멤버 쌍을 조회합니다.
-- SELECT m1.member_name AS member1, m2.member_name AS member2, m1.country
-- FROM Member m1
-- JOIN Member m2 ON m1.country = m2.country AND m1.id < m2.id;


-- ? LIKE
-- 포지션에 '보컬'이 있는 멤버를 조회합니다.
SELECT * FROM Member WHERE position LIKE '%보컬%';

-- 앨범 이름에 'Love'가 포함된 앨범을 조회합니다.
SELECT * FROM Album WHERE album_name LIKE '%Love%';


-- ? CASE
-- 앨범 판매량에 따라 등급을 매깁니다.
SELECT 
    album_name,
    sales_volume,
    CASE 
        WHEN sales_volume > 1000000 THEN '플래티넘'
        WHEN sales_volume > 500000 THEN '골드'
        ELSE '실버'
    END AS sales_grade
FROM Album;

-- 멤버의 출생 연도에 따라 세대를 구분합니다. (mz,alpah세대 기준 적어주기)
SELECT 
    member_name,
    birthday,
    CASE 
        WHEN strftime('%Y', birthday) >= '2013' THEN 'Alpha세대'
        WHEN strftime('%Y', birthday) >= '1997' AND strftime('%Y', birthday) <= '2012' THEN 'Z세대'
        WHEN strftime('%Y', birthday) >= '1981' AND strftime('%Y', birthday) <= '1996' THEN 'M세대'
        ELSE '기타'
    END AS generation
FROM Member;


-- ? SUBSTR 
-- 아티스트 그룹 이름의 첫 3글자를 추출합니다.
SELECT member_name, SUBSTR(position, 1, 2) AS position_short
FROM Member;

-- 앨범 발매 연도만 추출합니다.
SELECT album_name, SUBSTR(release_date, 1, 4) AS release_year
FROM Album;


-- -- ? COALESCE
-- -- 판매량이 NULL인 경우 0으로 대체하여 조회합니다.
-- SELECT album_name, COALESCE(sales_volume, 0) AS "Confirmed Sales"
-- FROM Album;

-- -- 포지션이 NULL인 경우 'Unknown'으로 대체하여 조회합니다.
-- SELECT member_name, COALESCE(position, 'Unknown') AS "Confirmed Position"
-- FROM Member;
