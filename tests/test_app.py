import pytest


class TestActivities:
    """Test cases for activities endpoints"""

    def test_get_activities(self, client):
        """Test GET /activities returns all activities"""
        response = client.get("/activities")
        assert response.status_code == 200
        
        activities = response.json()
        assert isinstance(activities, dict)
        assert "Tennis Team" in activities
        assert "Basketball Club" in activities
        assert "Drama Club" in activities
        
        # Check structure of an activity
        tennis = activities["Tennis Team"]
        assert "description" in tennis
        assert "schedule" in tennis
        assert "max_participants" in tennis
        assert "participants" in tennis
        assert isinstance(tennis["participants"], list)

    def test_signup_new_participant(self, client, reset_activities):
        """Test successfully signing up a new participant"""
        response = client.post(
            "/activities/Tennis Team/signup",
            params={"email": "newemail@mergington.edu"}
        )
        assert response.status_code == 200
        
        result = response.json()
        assert "message" in result
        assert "newemail@mergington.edu" in result["message"]
        
        # Verify participant was added
        activities_response = client.get("/activities")
        activities = activities_response.json()
        assert "newemail@mergington.edu" in activities["Tennis Team"]["participants"]

    def test_signup_already_registered(self, client, reset_activities):
        """Test signing up a participant who is already registered"""
        # alex@mergington.edu is already in Tennis Team
        response = client.post(
            "/activities/Tennis Team/signup",
            params={"email": "alex@mergington.edu"}
        )
        assert response.status_code == 400
        
        result = response.json()
        assert "already signed up" in result["detail"]

    def test_signup_nonexistent_activity(self, client):
        """Test signing up for a non-existent activity"""
        response = client.post(
            "/activities/Nonexistent Activity/signup",
            params={"email": "newemail@mergington.edu"}
        )
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]

    def test_unregister_participant(self, client, reset_activities):
        """Test successfully unregistering a participant"""
        # alex@mergington.edu is already in Tennis Team
        response = client.post(
            "/activities/Tennis Team/unregister",
            params={"email": "alex@mergington.edu"}
        )
        assert response.status_code == 200
        
        result = response.json()
        assert "message" in result
        assert "alex@mergington.edu" in result["message"]
        
        # Verify participant was removed
        activities_response = client.get("/activities")
        activities = activities_response.json()
        assert "alex@mergington.edu" not in activities["Tennis Team"]["participants"]

    def test_unregister_not_registered(self, client, reset_activities):
        """Test unregistering a participant who is not registered"""
        response = client.post(
            "/activities/Tennis Team/unregister",
            params={"email": "notregistered@mergington.edu"}
        )
        assert response.status_code == 400
        
        result = response.json()
        assert "not registered" in result["detail"]

    def test_unregister_nonexistent_activity(self, client):
        """Test unregistering from a non-existent activity"""
        response = client.post(
            "/activities/Nonexistent Activity/unregister",
            params={"email": "someone@mergington.edu"}
        )
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]

    def test_signup_and_unregister_flow(self, client, reset_activities):
        """Test complete flow: signup, verify, unregister, verify"""
        email = "testuser@mergington.edu"
        activity = "Art Studio"
        
        # Sign up
        signup_response = client.post(
            f"/activities/{activity}/signup",
            params={"email": email}
        )
        assert signup_response.status_code == 200
        
        # Verify signed up
        activities_response = client.get("/activities")
        activities = activities_response.json()
        assert email in activities[activity]["participants"]
        
        # Unregister
        unregister_response = client.post(
            f"/activities/{activity}/unregister",
            params={"email": email}
        )
        assert unregister_response.status_code == 200
        
        # Verify unregistered
        activities_response = client.get("/activities")
        activities = activities_response.json()
        assert email not in activities[activity]["participants"]

    def test_activity_availability(self, client, reset_activities):
        """Test that activities show correct availability"""
        response = client.get("/activities")
        activities = response.json()
        
        tennis = activities["Tennis Team"]
        expected_spots = tennis["max_participants"] - len(tennis["participants"])
        # We can't directly check spots_left from the API endpoint,
        # but we can verify the data structure is correct
        assert tennis["max_participants"] > 0
        assert len(tennis["participants"]) >= 0
        assert len(tennis["participants"]) <= tennis["max_participants"]


class TestRoot:
    """Test cases for root endpoint"""

    def test_root_redirect(self, client):
        """Test that GET / redirects to /static/index.html"""
        # Note: TestClient follows redirects by default
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"
