use wntrade;
show tables;
select * from wntrade.고객;

select 사원번호,이름,부서명
from 사원 left join 부서 
on 사원.부서번호=부서.부서번호;

SELECT  A.고객회사명, A.담당자명, A.마일리지
FROM 고객 A
LEFT JOIN 고객 B
ON A.마일리지 < B.마일리지
WHERE B.고객번호 IS NULL;

select 고객번호
       ,고객회사명
       ,담당자명
       ,마일리지
       ,등급명
 From 고객
      , 마일리지등급
Where 마일리지 between 하한마일리지 and 상한마일리지
and 담당자명 ='이은광'; 

select 부서명
       ,사원.*
from 사원 
right  join 부서
on 사원.부서번호= 부서.부서번호
where 사원.부서번호  is null;

select 고객.고객회사명, 고객.담당자명
from 고객 left join 주문 on  고객.고객번호 = 주문.고객번호
where 주문.주문번호 is null ;

select 사원.사원번호
      , 사원.이름
      , 상사.사원번호 as '상사의 사원번호'
      ,상사.이름 as '상사의 이름'
from 사원
left join 사원 as 상사 
on 사원.상사번호 = 상사.사원번호
where 사원.상사번호='';

select 고객번호
       ,고객회사명
       ,담당자명
       ,마일리지
from 고객
where 마일리지 =(select max(마일리지) from 고객 );

select max(마일리지)
from 고객;

select 고객회사명
       ,담당자명
from 고객
inner join 주문 
on 고객.고객번호=주문.고객번호
where 주문번호 = 'H0250';

select 고객회사명
      ,담당자명
from 고객
where 고객.고객번호 = (select 고객번호 
                     from 주문 
                     where  주문번호 = 'h0250');
                     
select 고객회사명
      ,담당자명
      ,마일리지
from 고객
where 마일리지 > some(select (마일리지)
                     from 고객 
                     where  도시 = '부산광역시');
                     
                     select count(*) as 주문건수
                     from 주문
                     where 고객번호 = any (select 고객번호
									   from 고객
                                       where  도시 = '부산광역시');
		
 select 도시 
        ,avg(마일리지) as 평균마일리지 
from 고객
group by 도시 
Having avg(마일리지)> (select avg(마일리지) from 고객 );

SELECT 담당자명
     , 고객회사명
     , 마일리지
     , 고객.도시
     , 도시_평균마일리지
     , 도시_평균마일리지 - 마일리지 AS 차이
FROM 고객
   , (SELECT 도시
           , AVG(마일리지) AS 도시_평균마일리지
      FROM 고객
      GROUP BY 도시
     ) AS 도시별요약
WHERE 고객.도시 = 도시별요약.도시;
 SELECT 고객번호
     , 담당자명
     , (SELECT MAX(주문일)
        FROM 주문
        WHERE 주문.고객번호 = 고객.고객번호
       ) AS 최종주문일
FROM 고객;