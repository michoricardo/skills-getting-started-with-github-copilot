"""
Happy path endpoint tests for the High School Management System API
Using AAA (Arrange-Act-Assert) pattern
"""

import pytest


class TestRootEndpoint:
    """Tests for GET /"""
    
    def test_root_redirects_to_static_index(self, client):
        # Arrange: No setup needed for redirect test
        
        # Act: Make request to root endpoint
        response = client.get("/", follow_redirects=False)
        
        # Assert: Verify redirect status and location
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"


class TestActivitiesEndpoint:
    """Tests for GET /activities"""
    
    def test_get_all_activities_returns_success(self, client):
        # Arrange: No specific setup needed
        
        # Act: Request all activities
        response = client.get("/activities")
        
        # Assert: Verify success status
        assert response.status_code == 200
    
    def test_get_all_activities_returns_correct_number(self, client):
        # Arrange: We know the app has 9 activities
        expected_count = 9
        
        # Act: Request all activities
        response = client.get("/activities")
        activities = response.json()
        
        # Assert: Verify all activities are returned
        assert len(activities) == expected_count
    
    def test_get_all_activities_contains_required_fields(self, client):
        # Arrange: Define required fields for each activity
        required_fields = {"description", "schedule", "max_participants", "participants"}
        
        # Act: Request all activities
        response = client.get("/activities")
        activities = response.json()
        
        # Assert: Verify each activity has required fields
        for activity_name, activity_data in activities.items():
            assert isinstance(activity_name, str)
            assert isinstance(activity_data, dict)
            assert required_fields.issubset(activity_data.keys())
            assert isinstance(activity_data["participants"], list)
            assert isinstance(activity_data["max_participants"], int)
    
    def test_get_all_activities_returns_specific_activities(self, client):
        # Arrange: Define activities that should exist
        expected_activities = {
            "Chess Club",
            "Programming Class",
            "Gym Class",
            "Basketball Team",
            "Soccer Club",
            "Art Club",
            "Drama Club",
            "Debate Club",
            "Science Club"
        }
        
        # Act: Request all activities
        response = client.get("/activities")
        activities = response.json()
        actual_activities = set(activities.keys())
        
        # Assert: Verify expected activities are present
        assert expected_activities == actual_activities


class TestSignupEndpoint:
    """Tests for POST /activities/{activity_name}/signup"""
    
    def test_signup_for_activity_success(self, client):
        # Arrange: Prepare signup data for an activity with available spots
        activity_name = "Basketball Team"
        email = "newstudent@mergington.edu"
        
        # Act: Send signup request
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Assert: Verify successful signup
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert email in data["message"]
        assert activity_name in data["message"]
    
    def test_signup_adds_participant_to_activity(self, client):
        # Arrange: Get initial participant list and prepare signup
        activity_name = "Soccer Club"
        email = "soccer_fan@mergington.edu"
        
        initial_response = client.get("/activities")
        initial_participants = initial_response.json()[activity_name]["participants"].copy()
        
        # Act: Sign up for activity
        client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Assert: Verify participant was added
        updated_response = client.get("/activities")
        updated_participants = updated_response.json()[activity_name]["participants"]
        assert email in updated_participants
        assert len(updated_participants) == len(initial_participants) + 1
    
    def test_signup_multiple_students_different_activities(self, client):
        # Arrange: Prepare data for multiple signups
        signup_data = [
            ("Basketball Team", "student1@mergington.edu"),
            ("Art Club", "student2@mergington.edu"),
            ("Drama Club", "student3@mergington.edu"),
        ]
        
        # Act: Sign up multiple students to different activities
        for activity_name, email in signup_data:
            response = client.post(
                f"/activities/{activity_name}/signup",
                params={"email": email}
            )
            assert response.status_code == 200
        
        # Assert: Verify all signups were successful
        activities_response = client.get("/activities")
        activities = activities_response.json()
        
        for activity_name, email in signup_data:
            assert email in activities[activity_name]["participants"]


class TestRemoveParticipantEndpoint:
    """Tests for DELETE /activities/{activity_name}/participants"""
    
    def test_remove_participant_success(self, client):
        # Arrange: Use an activity with existing participants
        activity_name = "Chess Club"
        email = "michael@mergington.edu"  # Known participant
        
        # Verify participant exists initially
        initial_response = client.get("/activities")
        assert email in initial_response.json()[activity_name]["participants"]
        
        # Act: Remove the participant
        response = client.delete(
            f"/activities/{activity_name}/participants",
            params={"email": email}
        )
        
        # Assert: Verify successful removal
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert email in data["message"]
        assert activity_name in data["message"]
    
    def test_remove_participant_actually_removes_participant(self, client):
        # Arrange: Identify participant to remove
        activity_name = "Programming Class"
        email = "emma@mergington.edu"  # Known participant
        
        initial_response = client.get("/activities")
        initial_count = len(initial_response.json()[activity_name]["participants"])
        
        # Act: Remove participant
        client.delete(
            f"/activities/{activity_name}/participants",
            params={"email": email}
        )
        
        # Assert: Verify participant was removed
        updated_response = client.get("/activities")
        updated_participants = updated_response.json()[activity_name]["participants"]
        updated_count = len(updated_participants)
        
        assert email not in updated_participants
        assert updated_count == initial_count - 1
    
    def test_remove_multiple_participants(self, client):
        # Arrange: Prepare participants to remove from an activity with multiple
        activity_name = "Gym Class"
        participants_to_remove = [
            "john@mergington.edu",
            "olivia@mergington.edu"
        ]
        
        initial_response = client.get("/activities")
        initial_count = len(initial_response.json()[activity_name]["participants"])
        
        # Act: Remove each participant
        for email in participants_to_remove:
            response = client.delete(
                f"/activities/{activity_name}/participants",
                params={"email": email}
            )
            assert response.status_code == 200
        
        # Assert: Verify all participants were removed
        updated_response = client.get("/activities")
        updated_participants = updated_response.json()[activity_name]["participants"]
        
        for email in participants_to_remove:
            assert email not in updated_participants
        
        assert len(updated_participants) == initial_count - len(participants_to_remove)
