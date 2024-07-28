# 웹 애플리케이션 프로젝트

이 프로젝트는 Flask와 SQLAlchemy를 사용하여 구축된 웹 애플리케이션입니다. 질문 답변 시스템, 블로그 기능, 그리고 SQL 문서 관리 기능을 포함하고 있습니다.

## 주요 기능

1. 관리자 시스템
2. 질문 답변 시스템
3. 블로그 기능
4. SQL 문서 관리

## 데이터베이스 구조

### AdminUser

-   관리자 계정 관리

### Question & Answer

-   질문 답변 시스템
-   파일 첨부 기능
-   좋아요 기능
-   답변의 계층 구조 지원

### Article & ArticleComment

-   블로그 기능
-   카테고리 및 태그 지원
-   댓글 시스템 (계층 구조)
-   조회수 및 좋아요 기능

### SqlDocCategory & SqlDoc

-   SQL 문서 관리 시스템
-   카테고리 계층 구조
-   문서 순서 관리

## 기술 스택

-   Backend: Flask
-   Database: SQLAlchemy ORM
-   Authentication: bcrypt for password hashing
-   ID Generation: nanoid
-   가상 환경: Miniconda

## 설치 및 실행 방법

1. Miniconda 설치:

    - [Miniconda 공식 웹사이트](https://docs.conda.io/en/latest/miniconda.html)에서 운영 체제에 맞는 버전을 다운로드하여 설치합니다.

2. 프로젝트 클론:

    ```
    mkdir Flask.WISE.IT.BE
    cd Flask.WISE.IT.BE
    git clone https://github.com/WISE-IT-TEAM/Flask.WISE.IT.BE.git .
    ```

3. Conda 환경 생성 및 활성화:

    ```
    conda create -n your-env-name python=3.12
    conda activate your-env-name
    ```

4. 의존성 설치:

    - 환경 설정 파일은 외부 문서를 참조해야 합니다. 해당 문서의 지침에 따라 필요한 패키지를 설치하세요.
    - 일반적으로 다음과 같은 명령어를 사용할 수 있습니다:
        ```
        pip install -r requirements.txt
        ```

5. 환경 변수 설정:

    - 필요한 환경 변수가 있다면 설정해주세요. (예: 데이터베이스 URL, 시크릿 키 등)

6. 데이터베이스 초기화:

    ```
    flask db upgrade
    ```

7. 애플리케이션 실행:
    ```
    flask run
    ```

자세한 설정 방법과 추가 정보는 Jira Confluence 문서를 참조하세요.

## 기여 방법

1. 이 저장소를 포크합니다.
2. 새 브랜치를 생성합니다: `git checkout -b feature/AmazingFeature`
3. 변경 사항을 커밋합니다: `git commit -m 'Add some AmazingFeature'`
4. 브랜치에 푸시합니다: `git push origin feature/AmazingFeature`
5. Pull Request를 생성합니다.

## 라이선스

이 프로젝트는 [MIT 라이선스](LICENSE)하에 배포됩니다.
