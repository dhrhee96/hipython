from weasyprint import HTML

html_content = """
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <title>이력서_이동현_운영및CS</title>
    <style>
        @page {
            size: A4;
            margin: 15mm;
            background-color: #ffffff;
        }
        body {
            font-family: 'NanumGothic', 'Malgun Gothic', sans-serif;
            line-height: 1.6;
            color: #333;
            margin: 0;
            padding: 0;
            font-size: 10pt;
        }
        .header {
            border-bottom: 2px solid #2c3e50;
            padding-bottom: 10px;
            margin-bottom: 20px;
        }
        .header h1 {
            margin: 0;
            font-size: 22pt;
            color: #2c3e50;
        }
        .contact-info {
            font-size: 9pt;
            color: #555;
            margin-top: 5px;
        }
        h2 {
            font-size: 14pt;
            border-left: 4px solid #2c3e50;
            padding-left: 8px;
            margin-top: 25px;
            margin-bottom: 10px;
            color: #2c3e50;
            background-color: #f8f9fa;
        }
        .summary {
            background-color: #f1f3f5;
            padding: 12px;
            border-radius: 4px;
            margin-bottom: 20px;
            font-weight: 500;
        }
        .section-content {
            margin-left: 5px;
        }
        .item {
            margin-bottom: 15px;
        }
        .item-title {
            font-weight: bold;
            font-size: 11pt;
            display: flex;
            justify-content: space-between;
        }
        .item-date {
            color: #777;
            font-size: 9pt;
        }
        .item-desc {
            margin-top: 5px;
            color: #444;
        }
        ul {
            margin-top: 5px;
            margin-bottom: 5px;
            padding-left: 20px;
        }
        li {
            margin-bottom: 3px;
        }
        .skills-grid {
            display: table;
            width: 100%;
        }
        .skill-row {
            display: table-row;
        }
        .skill-cat {
            display: table-cell;
            font-weight: bold;
            width: 100px;
            padding: 3px 0;
        }
        .skill-val {
            display: table-cell;
            padding: 3px 0;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>이 동 현 (Dong Hyun Rhee)</h1>
        <div class="contact-info">
            📧 dhrhee96@gmail.com | 📱 010-8215-3884 | 📍 대한민국 경기도
        </div>
    </div>

    <div class="summary">
        "수학적 논리로 이슈를 분석하고 데이터로 운영의 방향을 제시하는 운영 전문가 지원자입니다."<br>
       수학과 학석사 과정을 통해 다져진 문제 해결 능력과 Python/SQL 기반의 데이터 분석 역량을 보유하고 있습니다. 단순한 CS 응대를 넘어 유저 피드백 속의 패턴을 읽고, 논리적인 리포팅을 통해 서비스 품질을 높이는 '브릿지' 역할을 수행하고자 합니다.
    </div>

    <h2>핵심 역량 (Core Skills)</h2>
    <div class="section-content">
        <div class="skills-grid">
            <div class="skill-row">
                <div class="skill-cat">Analysis</div>
                <div class="skill-val">Python(Pandas, Scikit-learn), SQL, 데이터 통계 분석, 수치 모델링</div>
            </div>
            <div class="skill-row">
                <div class="skill-cat">Language</div>
                <div class="skill-val">영어(원어민 수준, 해외 거주 7년), 한국어(모국어)</div>
            </div>
            <div class="skill-row">
                <div class="skill-cat">Tools</div>
                <div class="skill-val">MS Office, LaTeX, Git </div>
            </div>
        </div>
    </div>

    <h2>전문 경력 및 활동 (Experience & Activities)</h2>
    <div class="section-content"> 
       <div class="item">
            <div class="item-title">
                <span>University of Manchester - PASS(Peer Assisted Study Sessions) Mentor</span>
                <span class="item-date">2018.09 – 2019.06</span>
            </div>
            <div class="item-desc">
                <ul>
                    <li>수학 전공 신입생 대상 학습 및 대학 생활 적응 멘토링 주도</li>
                    <li>복잡한 수학적 개념을 상대방의 눈높이에 맞춰 설명하는 커뮤니케이션 역량 강화</li>
                    <li>다양한 문화권의 학생들과 소통하며 갈등 조정 및 문제 해결 지원</li>
                </ul>
            </div>
        </div>
    </div>

    <h2>주요 프로젝트 (Analytical Projects)</h2>
    <div class="section-content">
        <div class="item">
            <div class="item-title">
                <span>데이터 기반 중고차 가격예측 모델 구축 프로젝트 (Python)</span>
                <span class="item-date">2026.03</span>
            </div>
            <div class="item-desc">
                <ul>
                    <li>Quantile XGBoost 및 Optuna를 활용한 예측 모델 개발</li>
                    <li>수많은 변수(Feature) 중 유의미한 상관관계를 가진 데이터를 선별하는 통계적 분석 수행</li>
                    <li><strong>운영 적용점:</strong> 게임 내 유저 이탈 징후 분석 및 비정상적인 재화 흐름(어뷰징) 탐지 시스템에 응용 가능한 분석 논리 보유</li>
                </ul>
            </div>
        </div>
    </div>

    <h2>학력 사항 (Education)</h2>
    <div class="section-content">
        <div class="item">
            <div class="item-title">
                <span>University of Manchester (UK) - Mathematics (Integrated Master's)</span>
                <span class="item-date">2017.09 – 2021.07 (중도귀국 후 수료)</span>
            </div>
            <div class="item-desc">
                주요 수강 과목:수치 해석,편미분 방정식
            </div>
        </div>
    </div>
    <h2>게임 경험 (Gaming Experience)</h2>
    <div class="section-content">
        <div class="item">
            <div class="item-title">
                <span>트릭컬 Re:vive  </span>
                <span class="item-date">2023.09 – 현재</span>
            </div>
            <div class="item-desc">
                <ul>
                    <li>유저 친화적 운영 정책에 대한 높은 이해도, 특히 게임 내부 사고가 터졌을때 빠른 피드백으로 유저들의 불만을 줄임 </li>
                    <li>캐릭터 특히 이드나 죠안같은 엘다인 캐릭터 확률이,타 3성캐릭터들에 비해서 압도적으로 낮은것을 경험</li>
                </ul>
            </div>
            <div class="item-title">
                <span>던전앤파이터  </span>
                <span class="item-date">2020.09 – 현재</span>
            </div>
            <div class="item-desc">
                <ul>
                    <li>현행 엔드 컨텐츠 다수 클리어 경험(바칼,안개신,나벨,이내 황혼전,디레지에)</li>
                    <li>딜 인플레이션을 일으키는 상품을 함부로 출시하면 안된다는것을 경험</li>
                    <li>현행 디렉터의 소통을 방식을 통해,일방적인 통보를 하면 유저들의 불만이 증가한다는 것을 경험</li>
                </ul>
            </div>
             <div class="item-title">
                <span>림버스 컴퍼니 </span>
                <span class="item-date">2020.09 – 현재</span>
            </div>
            <div class="item-desc">
                <ul>
                    <li>현행 엔드 컨텐츠 다수 클리어 경험(바칼,안개신,나벨,이내 황혼전,디레지에)</li>
                    <li>딜 인플레이션을 일으키는 상품을 함부로 출시하면 안된다는것을 경험</li>
                    <li>현행 디렉터의 소통을 방식을 통해,일방적인 통보를 하면 유저들의 불만이 증가한다는 것을 경험</li>
                </ul>
            </div>
         </div>
    </div>
    <h2>추가 정보 (Additional Information)</h2>
    <div class="section-content">
        <ul>
            <li><strong>취미:</strong> 실내/외 클라이밍 (문제 해결을 위한 집요함과 끈기를 배움)</li>
            <li><strong>강점:</strong> 4L(Liked, Learned, Lacked, Longed for) 회고법을 통한 자기 객관화 및 지속적 성장</li>
        </ul>
    </div>
    </body>
</html>
"""

with open("resume_donghyun.html", "w", encoding="utf-8") as f:
    f.write(html_content)

HTML(filename="resume_donghyun.html").write_pdf("Resume_DongHyunRhee_GameOps.pdf")