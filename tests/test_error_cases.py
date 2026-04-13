"""
Error and edge case tests for the High School Management System API
Using AAA (Arrange-Act-Assert) pattern
"""

import pytest


class TestSignupErrorCases:
    """Tests for error conditions in POST /activities/{activity_name}/signup"""
    
    def test_signup_nonexistent_activity_returns_404(self, client):
        # Arrange: Use activity name that doesn't exist
        activity_name = "Phantom Club"
        email = "student@mergington.edu"
        
        # Act: Attempt to sign up for non-existent activity
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Assert: Verify 404 error
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
    
    def test_signup_duplicate_email_returns_400(self, client):
        # Arrange: Use an existing participant
        activity_name = "Chess Club"
        email = "michael@mergington.edu"  # Already signed up
        
        # Verify participant already exists
        activities_response = client.get("/activities")
        assert email in activities_response.json()[activity_name]["participants"]
        
        # Act: Attempt duplicate signup
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Assert: Verify 400 error for duplicate
        assert response.status_code == 400
        assert "already signed up" in response.json()["detail"].lower()
    
    def test_signup_with_empty_email(self, client):
        # Arrange: Use empty email string
        activity_name = "Basketball Team"
        email = ""
        
        # Act: Attempt signup with empty email
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Assert: Verify it fails (behavior depends on validation)
        # Empty email should either be rejected or cause an issue
        assert response.status_code in [400, 422]  # Bad request or validation error
    
    def test_signup_case_sensitive_activity_names(self, client):
        # Arrange: Try different case for activity name
        activity_name_wrong_case = "chess club"  # lowercase
        email = "student@mergington.edu"
        
        # Act: Attempt signup with wrong case
        response = client.post(
            f"/activities/{activity_name_wrong_case}/signup",
            params={"email": email}
        )
        
        # Assert: Verify it fails (activity names are case-sensitive)
        assert response.status_code == 404


class TestRemoveParticipantErrorCases:
    """Tests for error conditions in DELETE /activities/{activity_name}/participants"""
    
    def test_remove_from_nonexistent_activity_returns_404(self, client):
        # Arrange: Use activity that doesn't exist
        activity_name = "Fake Club"
        email = "student@mergington.edu"
        
        # Act: Attempt to remove from non-existent activity
        response = client.delete(
            f"/activities/{activity_name}/participants",
            params={"email": email}
        )
        
        # Assert: Verify 404 error
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
    
    def test_remove_nonexistent_participant_returns_404(self, client):
        # Arrange: Use valid activity but participant not in it
        activity_name = "Basketball Team"
        email = "notamember@mergington.edu"
        
        # Verify participant doesn't exist
        activities_response = client.get("/activities")
        assert email not in activities_response.json()[activity_name]["participants"]
        
        # Act: Attempt to remove non-existent participant
        response = client.delete(
            f"/activities/{activity_name}/participants",
            params={"email": email}
        )
        
        # Assert: Verify 404 error
        assert response.status_code == 404
        assert "participant not found" in response.json()["detail"].lower()
    
    def test_remove_from_empty_activity(self, client):
        # Arrange: Use an activity with no participants
        activity_name = "Drama Club"  # Has no participants initially
        email = "anyone@mergington.edu"
        
        # Verify activity is empty
        activities_response = client.get("/activities")
        assert len(activities_response.json()[activity_name]["participants"]) == 0
        
        # Act: Attempt to remove from empty activity
        response = client.delete(
            f"/activities/{activity_name}/participants",
            params={"email": email}
        )
        
        # Assert: Verify 404 error
        assert response.status_code == 404
        assert "participant not found" in response.json()["detail"].lower()


class TestActivitiesCapacityEdgeCases:
    """Tests for edge cases around activity capacity"""
    
    def test_activities_have_different_capacities(self, client):
        # Arrange: Get all activities
        
        # Act: Request activities
        response = client.get("/activities")
        activities = response.json()
        
        # Assert: Verify activities have the expected capacities
        expected_capacities = {
            "Chess Club": 12,
            "Programming Class": 20,
            "Gym Class": 30,
            "Basketball Team": 15,
            "Soccer Club": 22,
            "Art Club": 18,
            "Drama Club": 20,
            "Debate Club": 16,
            "Science Club": 25
        }
        
        for activity_name, expected_max in expected_capacities.items():
            assert activities[activity_name]["max_participants"] == expected_max
    
    def test_participant_list_is_modifiable(self, client):
        # Arrange: Start with activity that has participants
        activity_name = "Chess Club"
        
        initial_response = client.get("/activities")
        initial_participants = initial_response.json()[activity_name]["participants"]
        initial_count = len(initial_participants)
        
        # Act: Remove a participant and re-check
        if initial_count > 0:
            email_to_remove = initial_participants[0]
            client.delete(
                f"/activities/{activity_name}/participants",
                params={"email": email_to_remove}
            )
            
            updated_response = client.get("/activities")
            updated_count = len(updated_response.json()[activity_name]["participants"])
            
            # Assert: Verify count decreased
            assert updated_count == initial_count - 1


class TestDataConsistencyEdgeCases:
    """Tests for data consistency and state management"""
    
    def test_signup_then_get_shows_updated_data(self, client):
        # Arrange: Choose activity and new email
        activity_name = "Art Club"
        email = "artlover@mergington.edu"
        
        # Act: Sign up
        client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Get activities after signup
        response = client.get("/activities")
        
        # Assert: Verify new participant appears in updated list
        assert email in response.json()[activity_name]["participants"]
    
    def test_remove_then_can_signup_again(self, client):
        # Arrange: Choose participant and activity
        activity_name = "Programming Class"
        email = "programmer@mergington.edu"
        
        # Sign up first
        client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Act: Remove the participant
        client.delete(
            f"/activities/{activity_name}/participants",
            params={"email": email}
        )
        
        # Attempt to sign up again
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Assert: Second signup should succeed
        assert response.status_code == 200
        
        # Verify participant is back in list
        activities_response = client.get("/activities")
        assert email in activities_response.json()[activity_name]["participants"]
    
    def test_state_isolation_between_tests(self, client):
        # Arrange: Each test should get a fresh copy of activities
        # This tests that our fixture properly resets state
        
        # Act: Get activities
        response = client.get("/activities")
        activities = response.json()
        
        # Assert: Activities should have their original state
        assert "michael@mergington.edu" in activities["Chess Club"]["participants"]
        assert "daniel@mergington.edu" in activities["Chess Club"]["participants"]
        assert len(activities["Basketball Team"]["participants"]) == 0
        assert len(activities["Soccer Club"]["participants"]) == 0


class TestResponseDataTypes:
    """Tests to verify response data types are correct"""
    
    def test_activity_data_types(self, client):
        # Arrange: Get response
        
        # Act: Request activities
        response = client.get("/activities")
        activities = response.json()
        
        # Assert: Verify data types
        for activity_name, activity_data in activities.items():
            assert isinstance(activity_name, str)
            assert isinstance(activity_data["description"], str)
            assert isinstance(activity_data["schedule"], str)
            assert isinstance(activity_data["max_participants"], int)
            assert isinstance(activity_data["participants"], list)
            # Verify participants are all strings (emails)
            assert all(isinstance(p, str) for p in activity_data["participants"])
    
    def test_signup_response_contains_message(self, client):
        # Arrange: Prepare signup
        activity_name = "Basketball Team"
        email = "newplayer@mergington.edu"
        
        # Act: Sign up
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Assert: Verify response structure
        assert isinstance(response.json(), dict)
        assert "message" in response.json()
        assert isinstance(response.json()["message"], str)
    
    def test_remove_response_contains_message(self, client):
        # Arrange: Prepare removal
        activity_name = "Gym Class"
        email = "john@mergington.edu"
        
        # Act: Remove participant
        response = client.delete(
            f"/activities/{activity_name}/participants",
            params={"email": email}
        )
        
        # Assert: Verify response structure
        assert isinstance(response.json(), dict)
        assert "message" in response.json()
        assert isinstance(response.json()["message"], str)
