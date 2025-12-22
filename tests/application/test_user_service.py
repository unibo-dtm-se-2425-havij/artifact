import unittest
from datetime import datetime

from havij.application.ports import UserAuthRecord
from havij.application.services.user_service import UserService
from havij.domain.model.user import UserProfile


class _InMemoryUserRepo:
    def __init__(self) -> None:
        self._auth_by_username: dict[str, UserAuthRecord] = {}
        self._profiles_by_id: dict[str, UserProfile] = {}

    def create_user(
        self,
        user_id: str,
        username: str,
        password_hash: str,
        salt: str,
        created_at: datetime,
    ) -> UserProfile:
        record = UserAuthRecord(
            user_id=user_id,
            username=username,
            password_hash=password_hash,
            salt=salt,
            created_at=created_at,
        )
        self._auth_by_username[username] = record
        profile = UserProfile(user_id=user_id, username=username, created_at=created_at)
        self._profiles_by_id[user_id] = profile
        return profile

    def get_auth_by_username(self, username: str) -> UserAuthRecord | None:
        return self._auth_by_username.get(username)

    def get_profile(self, user_id: str) -> UserProfile | None:
        return self._profiles_by_id.get(user_id)

    def count_users(self) -> int:
        return len(self._profiles_by_id)


class TestUserService(unittest.TestCase):
    def test_signup_creates_user_and_authenticates(self) -> None:
        repo = _InMemoryUserRepo()
        service = UserService(repo=repo)

        profile = service.signup("alice", "secret-pass")

        self.assertEqual(profile.username, "alice")
        self.assertEqual(repo.count_users(), 1)
        auth = repo.get_auth_by_username("alice")
        self.assertIsNotNone(auth)
        self.assertTrue(auth.password_hash)
        self.assertEqual(len(auth.salt), 32)

        authenticated = service.authenticate("alice", "secret-pass")
        self.assertIsNotNone(authenticated)
        self.assertEqual(authenticated.user_id, profile.user_id)

    def test_signup_rejects_empty_username_or_password(self) -> None:
        repo = _InMemoryUserRepo()
        service = UserService(repo=repo)

        with self.assertRaises(ValueError):
            service.signup("", "pw")

        with self.assertRaises(ValueError):
            service.signup("user", "")

    def test_signup_rejects_duplicate_username(self) -> None:
        repo = _InMemoryUserRepo()
        service = UserService(repo=repo)

        service.signup("alice", "pw1")
        with self.assertRaises(ValueError):
            service.signup("alice", "pw2")

    def test_authenticate_returns_none_for_wrong_password(self) -> None:
        repo = _InMemoryUserRepo()
        service = UserService(repo=repo)

        service.signup("alice", "pw1")
        result = service.authenticate("alice", "wrong")

        self.assertIsNone(result)

    def test_get_profile_returns_profile(self) -> None:
        repo = _InMemoryUserRepo()
        service = UserService(repo=repo)

        profile = service.signup("alice", "pw1")
        fetched = service.get_profile(profile.user_id)

        self.assertEqual(fetched, profile)

    def test_count_users_returns_total(self) -> None:
        repo = _InMemoryUserRepo()
        service = UserService(repo=repo)

        self.assertEqual(service.count_users(), 0)
        service.signup("alice", "pw1")
        service.signup("bob", "pw2")
        self.assertEqual(service.count_users(), 2)
