import requests
import sys
import json
from datetime import datetime

class ABADraftLobbyTester:
    def __init__(self, base_url="https://aba-draft-lobby.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.tests_run = 0
        self.tests_passed = 0
        self.lobby_code = None

    def run_test(self, name, method, endpoint, expected_status, data=None, params=None):
        """Run a single API test"""
        url = f"{self.api_url}/{endpoint}"
        headers = {'Content-Type': 'application/json'}

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, params=params)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers)

            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                try:
                    response_data = response.json()
                    print(f"   Response: {json.dumps(response_data, indent=2)[:200]}...")
                    return True, response_data
                except:
                    return True, {}
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"   Error: {error_data}")
                except:
                    print(f"   Error: {response.text}")
                return False, {}

        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, {}

    def test_root_endpoint(self):
        """Test root API endpoint"""
        success, response = self.run_test(
            "Root API Endpoint",
            "GET",
            "",
            200
        )
        return success

    def test_get_characters(self):
        """Test getting character roster"""
        success, response = self.run_test(
            "Get Characters",
            "GET", 
            "characters",
            200
        )
        if success and response:
            print(f"   Found {len(response)} anime series")
            total_chars = sum(len(series.get('characters', [])) for series in response)
            print(f"   Total characters: {total_chars}")
        return success

    def test_create_lobby(self):
        """Test creating a new lobby"""
        lobby_data = {
            "team1_name": "Test Team 1",
            "team2_name": "Test Team 2"
        }
        
        success, response = self.run_test(
            "Create Lobby",
            "POST",
            "lobbies",
            200,
            data=lobby_data
        )
        
        if success and response:
            self.lobby_code = response.get('code')
            print(f"   Created lobby with code: {self.lobby_code}")
            print(f"   Status: {response.get('status')}")
            print(f"   Current phase: {response.get('current_phase')}")
        
        return success

    def test_get_lobby(self):
        """Test getting lobby by code"""
        if not self.lobby_code:
            print("❌ No lobby code available for testing")
            return False
            
        success, response = self.run_test(
            "Get Lobby",
            "GET",
            f"lobbies/{self.lobby_code}",
            200
        )
        
        if success and response:
            print(f"   Lobby status: {response.get('status')}")
            print(f"   Team 1: {response.get('team1_name')} ({len(response.get('team1_players', []))} players)")
            print(f"   Team 2: {response.get('team2_name')} ({len(response.get('team2_players', []))} players)")
        
        return success

    def test_draft_action_ban(self):
        """Test draft ban action"""
        if not self.lobby_code:
            print("❌ No lobby code available for testing")
            return False
    def test_join_lobby(self):
        """Test joining a lobby"""
        if not self.lobby_code:
            print("❌ No lobby code available for testing")
            return False
            
        join_data = {
            "display_name": "TestPlayer1",
            "team": 1
        }
        
        success, response = self.run_test(
            "Join Lobby - Team 1",
            "POST",
            f"lobbies/{self.lobby_code}/join",
            200,
            data=join_data
        )
        
        if success and response:
            print(f"   Team 1 players: {response.get('team1_players')}")
            print(f"   Team 2 players: {response.get('team2_players')}")
        
        # Join team 2 as well
        join_data2 = {
            "display_name": "TestPlayer2", 
            "team": 2
        }
        
        success2, response2 = self.run_test(
            "Join Lobby - Team 2",
            "POST",
            f"lobbies/{self.lobby_code}/join",
            200,
            data=join_data2
        )
        
        return success and success2

    def test_start_draft(self):
        """Test starting the draft"""
        if not self.lobby_code:
            print("❌ No lobby code available for testing")
            return False
            
        success, response = self.run_test(
            "Start Draft",
            "POST",
            f"lobbies/{self.lobby_code}/start",
            200
        )
        
        if success and response:
            print(f"   Status after start: {response.get('status')}")
            print(f"   Current phase: {response.get('current_phase')}")
        
        return success
            
        action_data = {
            "character_id": "luffy",
            "action_type": "ban"
        }
        
        success, response = self.run_test(
            "Draft Action - Ban",
            "POST",
            f"lobbies/{self.lobby_code}/action",
            200,
            data=action_data
        )
        
        if success and response:
            print(f"   Phase after ban: {response.get('current_phase')}")
            print(f"   Team 1 bans: {response.get('team1_bans')}")
            print(f"   Team 2 bans: {response.get('team2_bans')}")
        
        return success

    def test_draft_action_pick(self):
        """Test draft pick action after progressing through phases"""
        if not self.lobby_code:
            print("❌ No lobby code available for testing")
            return False
        
        # First, let's do another ban to progress to pick phase
        ban_data = {
            "character_id": "zoro", 
            "action_type": "ban"
        }
        
        print("\n   Doing Team 2 ban first...")
        ban_success, ban_response = self.run_test(
            "Draft Action - Team 2 Ban",
            "POST",
            f"lobbies/{self.lobby_code}/action", 
            200,
            data=ban_data
        )
        
        if not ban_success:
            return False
            
        # Now do a pick (should be Team 1's turn to pick)
        pick_data = {
            "character_id": "goku",
            "action_type": "pick"
        }
        
        success, response = self.run_test(
            "Draft Action - Pick",
            "POST",
            f"lobbies/{self.lobby_code}/action",
            200,
            data=pick_data
        )
        
        if success and response:
            print(f"   Phase after pick: {response.get('current_phase')}")
            print(f"   Team 1 picks: {response.get('team1_picks')}")
            print(f"   Team 2 picks: {response.get('team2_picks')}")
        
        return success

    def test_reset_draft(self):
        """Test resetting the draft"""
        if not self.lobby_code:
            print("❌ No lobby code available for testing")
            return False
            
        success, response = self.run_test(
            "Reset Draft",
            "POST",
            f"lobbies/{self.lobby_code}/reset",
            200
        )
        
        if success and response:
            print(f"   Status after reset: {response.get('status')}")
            print(f"   Phase after reset: {response.get('current_phase')}")
            print(f"   Picks cleared: T1={len(response.get('team1_picks', []))}, T2={len(response.get('team2_picks', []))}")
            print(f"   Bans cleared: T1={len(response.get('team1_bans', []))}, T2={len(response.get('team2_bans', []))}")
        
        return success

    def test_get_draft_phases(self):
        """Test getting draft phases info"""
        success, response = self.run_test(
            "Get Draft Phases",
            "GET",
            "draft-phases",
            200
        )
        
        if success and response:
            print(f"   Found {len(response)} draft phases")
            for i, phase in enumerate(response[:3]):  # Show first 3 phases
                print(f"   Phase {i}: {phase.get('action')} - Team {phase.get('team')} (count: {phase.get('count')})")
        
        return success

    def test_invalid_lobby_code(self):
        """Test getting non-existent lobby"""
        success, response = self.run_test(
            "Invalid Lobby Code",
            "GET",
            "lobbies/INVALID",
            404
        )
        return success

    def test_invalid_character_action(self):
        """Test invalid character action"""
        if not self.lobby_code:
            print("❌ No lobby code available for testing")
            return False
            
        # Try to pick an already banned character
        action_data = {
            "character_id": "luffy",  # This was banned earlier
            "action_type": "ban"
        }
        
        success, response = self.run_test(
            "Invalid Character Action",
            "POST",
            f"lobbies/{self.lobby_code}/action",
            400,
            data=action_data
        )
        return success

def main():
    print("🚀 Starting ABA Draft Lobby API Tests")
    print("=" * 50)
    
    tester = ABADraftLobbyTester()
    
    # Run all tests
    tests = [
        tester.test_root_endpoint,
        tester.test_get_characters,
        tester.test_create_lobby,
        tester.test_get_lobby,
        tester.test_join_lobby,
        tester.test_start_draft,
        tester.test_draft_action_ban,
        tester.test_draft_action_pick,
        tester.test_reset_draft,
        tester.test_get_draft_phases,
        tester.test_invalid_lobby_code,
        tester.test_invalid_character_action,
    ]
    
    for test in tests:
        try:
            test()
        except Exception as e:
            print(f"❌ Test {test.__name__} failed with exception: {e}")
            tester.tests_run += 1
    
    # Print results
    print("\n" + "=" * 50)
    print(f"📊 Tests completed: {tester.tests_passed}/{tester.tests_run}")
    print(f"Success rate: {(tester.tests_passed/tester.tests_run*100):.1f}%")
    
    if tester.lobby_code:
        print(f"🔗 Test lobby code: {tester.lobby_code}")
    
    return 0 if tester.tests_passed == tester.tests_run else 1

if __name__ == "__main__":
    sys.exit(main())