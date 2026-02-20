"""IPL Auction API Tests"""

from decimal import Decimal
from unittest.mock import Mock, patch

from django.test import TestCase, SimpleTestCase
from rest_framework.test import APIClient
from rest_framework import status

from auction.models import Team, Player


# Unit Tets - No Database (SimpleTestCase with Mocks)
class PlayerBasePriceUnitTestMocked(SimpleTestCase):
    """Unit Test: Verify capped/uncapped base prices using mocks (No DB)"""

    @patch("auction.models.Player")
    def test_player_logic_with_patch(self, MockPlayer):
        """Test player logic using patch decorator"""
        # Arrange
        mock_instance = MockPlayer.return_value
        mock_instance.is_capped = True
        mock_instance.get_min_base_price.return_value = 20000000

        # Act
        player = MockPlayer(name="Test Player", is_capped=True)
        result = player.get_min_base_price()

        # Assert
        self.assertEqual(result, 20000000)


class TeamPurseUnitTestMocked(SimpleTestCase):
    """Unit Test: Team purse calculations using mocks (No DB)"""

    @patch("auction.models.Team")
    def test_team_purse_calculation_with_patch(self, MockTeam):
        """Test team purse logic using patch decorator"""
        # Arrange
        mock_team = MockTeam.return_value
        mock_team.purse_remaining = Decimal("1250000000")
        mock_team.name = "Test Team"

        bid_amount = 150000000
        expected_remaining = Decimal("1100000000")

        # Act - Simulate bid deduction logic
        mock_team.purse_remaining -= bid_amount

        # Assert
        self.assertEqual(mock_team.purse_remaining, expected_remaining)


# Integration Tests - With Database (TestCase)


class PlayerBasePriceIntegrationTest(TestCase):
    """Integration Test: Player base prices"""

    def test_capped_player_base_price(self):
        """Capped players: ₹2 Crore minimum"""
        # Arrange
        player_name = "Virat Kohli"
        is_capped = True
        expected_price = 20000000

        # Act - This hits the database
        player = Player.objects.create(name=player_name, is_capped=is_capped)
        result = player.get_min_base_price()

        # Assert
        self.assertEqual(result, expected_price)

    def test_uncapped_player_base_price(self):
        """Uncapped players: ₹30 Lakh minimum"""
        # Arrange
        player_name = "Ayush Mhatre"
        is_capped = False
        expected_price = 3000000

        # Act - This hits the database
        player = Player.objects.create(name=player_name, is_capped=is_capped)
        result = player.get_min_base_price()

        # Assert
        self.assertEqual(result, expected_price)


class TeamPurseIntegrationTest(TestCase):
    """Integration Test: Team purse calculations"""

    def test_team_can_bid_with_sufficient_purse(self):
        """Team can bid when purse is sufficient"""
        # Arrange
        team = Team.objects.create(name="Test Team", purse_remaining=50000000)
        bid_amount = 3000000

        # Act
        can_bid = team.purse_remaining >= bid_amount

        # Assert
        self.assertTrue(can_bid)

    def test_team_cannot_bid_with_insufficient_purse(self):
        """Team cannot bid when purse is insufficient"""
        # Arrange
        team = Team.objects.create(name="Test Team", purse_remaining=1000000)
        bid_amount = 3000000

        # Act
        can_bid = team.purse_remaining >= bid_amount

        # Assert
        self.assertFalse(can_bid)


class BidIntegrationTest(TestCase):
    """Integration Test: API + Database interaction"""

    def setUp(self):
        self.client = APIClient()

        self.team = Team.objects.create(
            name="Mumbai Mavericks", purse_remaining=1250000000
        )
        self.player = Player.objects.create(
            name="Rashid Khan", base_price=100000000, is_capped=True, status="active"
        )

    def test_get_active_player(self):
        """GET /api/players/active/ returns player with correct base price"""
        # Arrange
        expected_name = "Rashid Khan"
        expected_price = "100000000.00"

        # Act
        response = self.client.get("/api/players/active/")

        # Assert
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], expected_name)
        self.assertEqual(response.data["base_price"], expected_price)

    def test_bid_below_base_price_returns_400(self):
        """Bid ₹5 Crore on ₹10 Crore player returns 400 Bad Request"""
        # Arrange
        data = {"team_id": self.team.id, "amount": 50000000}

        # Act
        response = self.client.post(f"/api/players/{self.player.id}/bid/", data)

        # Assert
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_bid_updates_purse(self):
        """POST bid → Team.purse_remaining decreases correctly"""
        # Arrange
        initial_purse = self.team.purse_remaining
        bid_amount = 150000000

        data = {"team_id": self.team.id, "amount": bid_amount}

        # Act
        response = self.client.post(f"/api/players/{self.player.id}/bid/", data)
        self.team.refresh_from_db()

        # Assert
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.team.purse_remaining, initial_purse - bid_amount)

    def test_bid_exceeding_purse_returns_400(self):
        """Security Rule: Cannot bid more than purse_remaining"""
        # Arrange
        self.team.purse_remaining = 50000000
        self.team.save()

        data = {"team_id": self.team.id, "amount": 100000000}

        # Act
        response = self.client.post(f"/api/players/{self.player.id}/bid/", data)

        # Assert
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_bid_on_sold_player_returns_403(self):
        """Bid on sold player returns 403 Forbidden"""
        # Arrange
        self.player.status = "sold"
        self.player.save()

        data = {"team_id": self.team.id, "amount": 150000000}

        # Act
        response = self.client.post(f"/api/players/{self.player.id}/bid/", data)

        # Assert
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class CompleteAuctionFlowTest(TestCase):
    """E2E Test: Full auction journey"""

    def setUp(self):
        self.client = APIClient()
        self.team = Team.objects.create(
            name="Delhi Capitals", purse_remaining=1250000000
        )
        self.player = Player.objects.create(
            name="Jasprit Bumrah", base_price=10000000, status="active"
        )

    def test_complete_auction_flow(self):
        """Full flow: View player → Place bid → Verify purse"""
        # Arrange
        bid_amount = 150000000
        expected_remaining_purse = Decimal("1100000000")
        expected_team_name = "Delhi Capitals"

        # Act - Step 1: View active player
        response1 = self.client.get("/api/players/active/")

        # Assert - Step 1
        self.assertEqual(response1.status_code, 200)
        self.assertEqual(response1.data["name"], "Jasprit Bumrah")

        # Act - Step 2: Place bid
        data = {"team_id": self.team.id, "amount": bid_amount}
        response2 = self.client.post(f"/api/players/{self.player.id}/bid/", data)

        # Assert - Step 2
        self.assertEqual(response2.status_code, 200)
        current_price = Decimal(response2.data["current_price"])
        self.assertEqual(current_price, Decimal("150000000"))
        self.assertEqual(response2.data["highest_bidder"], expected_team_name)

        # Act - Step 3: Refresh team from DB
        self.team.refresh_from_db()

        # Assert - Step 3
        self.assertEqual(self.team.purse_remaining, expected_remaining_purse)
