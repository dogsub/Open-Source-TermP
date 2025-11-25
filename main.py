import os
import argparse
import json
import requests

from src.READMECreater.GithubFetcher import DownloadRepoFiles
from src.READMECreater.READMEGenerator import GenerateREADME
from src.TagCreater.Models import ModelThreading
from src.Utils.GetImage import GetImageInGithub


def ensure_dir(path):
    """디렉터리가 존재하지 않으면 생성합니다.

    Args:
        path (str): 생성할 디렉터리 경로
    """
    os.makedirs(path, exist_ok=True)


def save_text(path, text):
    """텍스트 내용을 UTF-8로 파일에 저장합니다.

    Args:
        path (str): 저장할 파일 경로
        text (str): 파일에 쓸 텍스트
    """
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)


def download_file(url, dest_path):
    """URL에서 파일을 다운로드하여 지정된 경로에 저장합니다.

    이미지 다운로드에서 사용되며, 실패 시 False를 반환합니다.

    Args:
        url (str): 다운로드할 파일의 URL
        dest_path (str): 저장할 로컬 경로

    Returns:
        bool: 다운로드 성공 여부
    """
    if not url:
        return False
    try:
        resp = requests.get(url, stream=True, timeout=30)
        resp.raise_for_status()
        with open(dest_path, "wb") as fh:
            for chunk in resp.iter_content(8192):
                fh.write(chunk)
        return True
    except Exception as e:
        print(f"Failed to download image: {e}")
        return False


def main():
    # 명령행 파서 설정
    parser = argparse.ArgumentParser(
        description="Generate README, tags, and choose image for a GitHub repo."
    )
    parser.add_argument(
        "repo", help="GitHub repository URL (e.g. https://github.com/owner/repo)"
    )
    parser.add_argument(
        "--out", default="output", help="Output directory to save results"
    )
    parser.add_argument(
        "--no-readme", action="store_true", help="Skip README generation"
    )
    parser.add_argument("--no-tags", action="store_true", help="Skip tag extraction")
    parser.add_argument("--no-image", action="store_true", help="Skip image fetching")
    args = parser.parse_args()

    # 입력값 및 출력 디렉터리 준비
    repo = args.repo
    outdir = os.path.abspath(args.out)
    ensure_dir(outdir)

    # 저장할 폴더 이름을 정규화 (owner/repo -> owner__repo)
    repo_name = (
        repo.rstrip("/\n").replace("https://github.com/", "").replace(".git", "")
    )
    repo_dir = os.path.join(outdir, repo_name.replace("/", "__"))
    ensure_dir(repo_dir)

    # 저장소 파일 다운로드
    print(f"Fetching repository files for: {repo}")
    try:
        files = DownloadRepoFiles(repo)
        print(f"Fetched {len(files)} code files.")
    except Exception as e:
        print(f"Error fetching repository files: {e}")
        files = []

    # README 생성 (외부 LLM API 사용 가능)
    readme_path = os.path.join(repo_dir, "GENERATED_README.md")
    if not args.no_readme:
        try:
            print("Generating README (may call external API)...")
            readme_text = GenerateREADME(repo, files)
            save_text(readme_path, readme_text)
            print(f"Saved generated README to: {readme_path}")
        except Exception as e:
            print(f"README generation failed: {e}")
    else:
        print("Skipping README generation.")

    # README에서 태그(기술 스택) 추출 (멀티 모델 호출)
    tags_path = os.path.join(repo_dir, "TAGS.json")
    if not args.no_tags:
        try:
            print("Running tag extraction models (may call external APIs)...")
            response = ModelThreading(repo)
            # ModelThreading의 반환값은 response-like 객체일 수 있으므로 텍스트를 추출
            tags_text = None
            if hasattr(response, "text"):
                tags_text = response.text
            else:
                tags_text = str(response)

            # 모델 출력이 JSON이면 파싱, 아니면 raw로 저장
            try:
                tags_json = json.loads(tags_text)
            except Exception:
                tags_json = {"raw": tags_text}

            save_text(tags_path, json.dumps(tags_json, ensure_ascii=False, indent=2))
            print(f"Saved tags output to: {tags_path}")
        except Exception as e:
            print(f"Tag extraction failed: {e}")
    else:
        print("Skipping tag extraction.")

    # 저장소에서 대표 이미지 선택 및 다운로드
    if not args.no_image:
        try:
            print("Choosing image from repository (README or repo files)...")
            img_url = GetImageInGithub(repo)
            if img_url:
                ext = os.path.splitext(img_url)[1].split("?")[0] or ".jpg"
                img_dest = os.path.join(repo_dir, f"repo_image{ext}")
                ok = download_file(img_url, img_dest)
                if ok:
                    print(f"Saved image to: {img_dest}")
                else:
                    print("Image download failed.")
            else:
                print("No image found for repository.")
        except Exception as e:
            print(f"Image fetching failed: {e}")
    else:
        print("Skipping image fetching.")

    print("Done.")


if __name__ == "__main__":
    main()
