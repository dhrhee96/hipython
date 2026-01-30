select * from 고객;
select 고객번호
       ,고객회사명 as 이름
      ,담당자명
      ,마일리지 as 포인트
from 고객;

select 제품명
,format(단가,0)
,format(재고,0) as "구매 가능 수량" 
,format(단가*재고,0) as "주문 가능 금액"
from 제품;

SELECT 제품번호 
       ,단가
       ,주문수량
       ,할인율
       ,format(단가*주문수량*(1-할인율),0) as "주문 금액"
       ,format(단가*할인율,0) as "할인 금액"
From 주문세부;