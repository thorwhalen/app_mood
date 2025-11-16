import { Box, Typography, Card, CardContent, Grid, Button } from '@mui/material'
import { Link } from 'react-router-dom'
import {
  Psychology as PsychologyIcon,
  Analytics as AnalyticsIcon,
  History as HistoryIcon,
  Newspaper as NewspaperIcon,
} from '@mui/icons-material'

export default function HomePage() {
  return (
    <Box>
      <Typography variant="h3" gutterBottom>
        Welcome to Mood
      </Typography>
      <Typography variant="body1" paragraph>
        Build and deploy machine learning models for financial sentiment analysis.
        Define custom semantic attributes, generate training data, train models,
        and analyze text sentiment.
      </Typography>

      <Grid container spacing={3} sx={{ mt: 2 }}>
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <PsychologyIcon sx={{ fontSize: 40, color: 'primary.main', mb: 2 }} />
              <Typography variant="h5" gutterBottom>
                Define Moods
              </Typography>
              <Typography variant="body2" paragraph>
                Create custom semantic attributes (moods) to detect specific
                sentiments in financial text.
              </Typography>
              <Button component={Link} to="/moods" variant="contained">
                Manage Moods
              </Button>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <AnalyticsIcon sx={{ fontSize: 40, color: 'primary.main', mb: 2 }} />
              <Typography variant="h5" gutterBottom>
                Analyze Text
              </Typography>
              <Typography variant="body2" paragraph>
                Use trained models to analyze sentiment in financial text and
                get scores from 0 to 1.
              </Typography>
              <Button component={Link} to="/analysis" variant="contained">
                Start Analysis
              </Button>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <NewspaperIcon sx={{ fontSize: 40, color: 'primary.main', mb: 2 }} />
              <Typography variant="h5" gutterBottom>
                Financial Headlines
              </Typography>
              <Typography variant="body2" paragraph>
                Quick analysis of current financial headlines with sentiment
                scores from -10 to +10.
              </Typography>
              <Button component={Link} to="/headlines" variant="contained">
                View Headlines
              </Button>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <HistoryIcon sx={{ fontSize: 40, color: 'primary.main', mb: 2 }} />
              <Typography variant="h5" gutterBottom>
                Analysis History
              </Typography>
              <Typography variant="body2" paragraph>
                Browse past analyses and track sentiment trends over time.
              </Typography>
              <Button component={Link} to="/history" variant="contained">
                View History
              </Button>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  )
}
