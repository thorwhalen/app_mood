import { BrowserRouter as Router, Routes, Route, useNavigate } from 'react-router-dom'
import { Container, AppBar, Toolbar, Typography, Box, Button, IconButton, Menu, MenuItem } from '@mui/material'
import { AccountCircle } from '@mui/icons-material'
import { useState } from 'react'
import HomePage from './pages/HomePage'
import MoodsPage from './pages/MoodsPage'
import MoodDetailPage from './pages/MoodDetailPage'
import AnalysisPage from './pages/AnalysisPage'
import HeadlinesPage from './pages/HeadlinesPage'
import HistoryPage from './pages/HistoryPage'
import LoginPage from './pages/LoginPage'
import RegisterPage from './pages/RegisterPage'
import AdminPage from './pages/AdminPage'
import Navigation from './components/Navigation'
import { authService } from './services/auth'

function UserMenu() {
  const navigate = useNavigate()
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null)
  const isAuthenticated = authService.isAuthenticated()

  const handleMenu = (event: React.MouseEvent<HTMLElement>) => {
    setAnchorEl(event.currentTarget)
  }

  const handleClose = () => {
    setAnchorEl(null)
  }

  const handleLogout = () => {
    authService.logout()
    handleClose()
    navigate('/login')
    window.location.reload() // Refresh to clear state
  }

  if (!isAuthenticated) {
    return (
      <Box>
        <Button color="inherit" onClick={() => navigate('/login')}>
          Login
        </Button>
        <Button color="inherit" onClick={() => navigate('/register')}>
          Register
        </Button>
      </Box>
    )
  }

  return (
    <Box>
      <IconButton
        size="large"
        onClick={handleMenu}
        color="inherit"
      >
        <AccountCircle />
      </IconButton>
      <Menu
        anchorEl={anchorEl}
        open={Boolean(anchorEl)}
        onClose={handleClose}
      >
        <MenuItem onClick={handleLogout}>Logout</MenuItem>
      </Menu>
    </Box>
  )
}

function App() {
  return (
    <Router>
      <Box sx={{ flexGrow: 1 }}>
        <AppBar position="static">
          <Toolbar>
            <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
              Mood - Financial Sentiment Analysis
            </Typography>
            <UserMenu />
          </Toolbar>
        </AppBar>
        <Navigation />
        <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
          <Routes>
            <Route path="/" element={<HomePage />} />
            <Route path="/login" element={<LoginPage />} />
            <Route path="/register" element={<RegisterPage />} />
            <Route path="/moods" element={<MoodsPage />} />
            <Route path="/moods/:id" element={<MoodDetailPage />} />
            <Route path="/analysis" element={<AnalysisPage />} />
            <Route path="/headlines" element={<HeadlinesPage />} />
            <Route path="/history" element={<HistoryPage />} />
            <Route path="/admin" element={<AdminPage />} />
          </Routes>
        </Container>
      </Box>
    </Router>
  )
}

export default App
