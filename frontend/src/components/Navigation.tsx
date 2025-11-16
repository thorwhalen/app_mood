import { Link } from 'react-router-dom'
import { Box, Tabs, Tab } from '@mui/material'
import { useLocation } from 'react-router-dom'

export default function Navigation() {
  const location = useLocation()

  const getTabValue = () => {
    const path = location.pathname
    if (path === '/') return 0
    if (path.startsWith('/moods')) return 1
    if (path === '/analysis') return 2
    if (path === '/headlines') return 3
    if (path === '/history') return 4
    if (path === '/admin') return 5
    return 0
  }

  return (
    <Box sx={{ borderBottom: 1, borderColor: 'divider', bgcolor: 'background.paper' }}>
      <Tabs value={getTabValue()} centered>
        <Tab label="Home" component={Link} to="/" />
        <Tab label="Moods" component={Link} to="/moods" />
        <Tab label="Analysis" component={Link} to="/analysis" />
        <Tab label="Headlines" component={Link} to="/headlines" />
        <Tab label="History" component={Link} to="/history" />
        <Tab label="Admin" component={Link} to="/admin" />
      </Tabs>
    </Box>
  )
}
