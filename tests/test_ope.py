from pathlib import Path

import pytest

import kon.ope as ope


def test_ope_get_git_root_dir(tmp_path: Path):
    repo = tmp_path / "repo"
    deep_dir = repo / ".git" / "deep"
    deep_dir.mkdir(parents=True)
    assert ope.get_git_root_dir(str(deep_dir)) == str(repo)


# def test_ope_get_stop_directory(cwd: str) -> str:
#     pass


def test_ope_get_bash_dir_win(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(ope, "_IS_WINDOWS", True)
    bin_dir = tmp_path / "Git" / "bin"
    bin_dir.mkdir(parents=True)
    bash_path = bin_dir / "bash.exe"
    bash_path.write_text("", encoding="utf-8")
    monkeypatch.setenv("PROGRAMFILES", str(tmp_path))
    assert ope.get_bash_dir() == str(tmp_path / "Git" / "bin" / "bash.exe")


def test_ope_get_bash_dir_posix(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(ope, "_IS_WINDOWS", False)
    monkeypatch.setenv("SHELL", "/usr/local/bin/fish")
    assert ope.get_bash_dir() == "/usr/local/bin/fish"


def test_ope_get_bash_dir_posix_fallback(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(ope, "_IS_WINDOWS", False)
    monkeypatch.delenv("SHELL", raising=False)
    assert ope.get_bash_dir() == "/bin/bash"


def test_ope_get_bash_dir_posix_fallback_empty(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(ope, "_IS_WINDOWS", False)
    monkeypatch.setenv("SHELL", "")
    assert ope.get_bash_dir() == "/bin/bash"


def test_ope_get_config_dir(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    repo = tmp_path / "repo"
    config_dir = repo / ".config" / "kon"
    config_dir.mkdir(parents=True)
    if ope.is_windows():
        monkeypatch.setenv("USERPROFILE", str(repo))
    else:
        monkeypatch.setenv("HOME", str(repo))
    assert ope.get_config_dir() == str(config_dir)


def test_ope_get_tools_dir(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    repo = tmp_path / "repo"
    tools_dir = repo / ".config" / "kon" / "bin"
    tools_dir.mkdir(parents=True)
    if ope.is_windows():
        monkeypatch.setenv("USERPROFILE", str(repo))
    else:
        monkeypatch.setenv("HOME", str(repo))
    assert ope.get_tools_dir() == str(tools_dir)


def test_ope_get_executable_ext_win(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(ope, "_IS_WINDOWS", True)
    assert ope.get_executable_ext() == "exe"


def test_ope_get_executable_ext_posix(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(ope, "_IS_WINDOWS", False)
    assert ope.get_executable_ext() == ""


def test_ope_shorten_dir():
    assert ope.shorten_dir(ope.get_config_dir()) == str(Path("~/.config/kon"))


def test_ope_as_posix_dir():
    assert ope.as_posix_dir("c:\\test\\..\\test\\t.py") == "c:/test/../test/t.py"
    assert ope.as_posix_dir("/etc/test/p") == "/etc/test/p"
