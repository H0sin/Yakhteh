import React from "react";
import { Box, Container, Typography, Button } from "@mui/material";
import { useAuth } from "../contexts/AuthContext";

const Dashboard: React.FC = () => {
  const { logout } = useAuth();

  const handleLogout = () => {
    logout();
  };

  return (
    <Container maxWidth="lg">
      <Box sx={{ mt: 4, mb: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          Yakhteh Dashboard
        </Typography>
        <Typography variant="body1" gutterBottom>
          Welcome to your medical platform dashboard.
        </Typography>
        <Button variant="outlined" onClick={handleLogout} sx={{ mt: 2 }}>
          Logout
        </Button>
      </Box>
    </Container>
  );
};

export default Dashboard;