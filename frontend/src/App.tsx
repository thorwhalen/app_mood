import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import { Container, AppBar, Toolbar, Typography, Box } from '@mui/material'
import HomePage from './pages/HomePage'
import MoodsPage from './pages/MoodsPage'
import MoodDetailPage from './pages/MoodDetailPage'
import AnalysisPage from './pages/AnalysisPage'
import HeadlinesPage from './pages/HeadlinesPage'
import HistoryPage from './pages/HistoryPage'
import Navigation from './components/Navigation'

function App() {
  return (
    <Router>
      <Box sx={{ flexGrow: 1 }}>
        <AppBar position="static">
          <Toolbar>
            <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
              Mood - Financial Sentiment Analysis
            </Typography>
          </Toolbar>
        </AppBar>
        <Navigation />
        <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
          <Routes>
            <Route path="/" element={<HomePage />} />
            <Route path="/moods" element={<MoodsPage />} />
            <Route path="/moods/:id" element={<MoodDetailPage />} />
            <Route path="/analysis" element={<AnalysisPage />} />
            <Route path="/headlines" element={<HeadlinesPage />} />
            <Route path="/history" element={<HistoryPage />} />
          </Routes>
        </Container>
      </Box>
    </Router>
  )
}

export default App
