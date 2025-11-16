import { useQuery } from '@tanstack/react-query'
import {
  Box,
  Typography,
  Card,
  CardContent,
  CircularProgress,
  Alert,
  Chip,
  Grid,
} from '@mui/material'
import { analysisApi } from '@/services/api'

export default function HeadlinesPage() {
  const { data: headlines, isLoading, error } = useQuery({
    queryKey: ['headlines'],
    queryFn: () => analysisApi.headlines().then((res) => res.data),
  })

  const getScoreColor = (score: number) => {
    if (score < -3) return 'error'
    if (score < 3) return 'default'
    return 'success'
  }

  const getScoreLabel = (score: number) => {
    if (score < -5) return 'Very Negative'
    if (score < -2) return 'Negative'
    if (score < 2) return 'Neutral'
    if (score < 5) return 'Positive'
    return 'Very Positive'
  }

  if (isLoading) {
    return (
      <Box display="flex" justifyContent="center" p={4}>
        <CircularProgress />
      </Box>
    )
  }

  if (error) {
    return (
      <Alert severity="error">
        Failed to load headlines. Make sure you have configured your OpenAI API key.
      </Alert>
    )
  }

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Financial Headlines
      </Typography>
      <Typography variant="body1" paragraph>
        Current financial headlines with sentiment analysis (scores from -10 to +10).
      </Typography>

      <Grid container spacing={2}>
        {headlines?.map((headline, index) => (
          <Grid item xs={12} key={index}>
            <Card>
              <CardContent>
                <Box display="flex" justifyContent="space-between" alignItems="center">
                  <Box flex={1}>
                    <Typography variant="h6" gutterBottom>
                      {headline.headline}
                    </Typography>
                    {headline.source && (
                      <Typography variant="caption" color="text.secondary">
                        Source: {headline.source}
                      </Typography>
                    )}
                  </Box>
                  <Box ml={2} textAlign="right">
                    <Typography
                      variant="h4"
                      color={
                        headline.sentiment_score < -3
                          ? 'error.main'
                          : headline.sentiment_score < 3
                          ? 'text.secondary'
                          : 'success.main'
                      }
                    >
                      {headline.sentiment_score > 0 ? '+' : ''}
                      {headline.sentiment_score.toFixed(1)}
                    </Typography>
                    <Chip
                      label={getScoreLabel(headline.sentiment_score)}
                      size="small"
                      color={getScoreColor(headline.sentiment_score)}
                    />
                  </Box>
                </Box>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>
    </Box>
  )
}
