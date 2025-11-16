import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import {
  Box,
  Typography,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  CircularProgress,
  Alert,
  Chip,
} from '@mui/material'
import { moodsApi, analysisApi } from '@/services/api'

export default function HistoryPage() {
  const [selectedMoodId, setSelectedMoodId] = useState<string>('')

  const { data: moods } = useQuery({
    queryKey: ['moods'],
    queryFn: () => moodsApi.list().then((res) => res.data),
  })

  const { data: analyses, isLoading } = useQuery({
    queryKey: ['analyses', selectedMoodId],
    queryFn: () =>
      analysisApi
        .list(selectedMoodId || undefined)
        .then((res) => res.data),
  })

  const getScoreColor = (score: number) => {
    if (score < 0.3) return 'error'
    if (score < 0.7) return 'warning'
    return 'success'
  }

  const getMoodName = (moodId: string) => {
    return moods?.find((m) => m.id === moodId)?.name || moodId
  }

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Analysis History
      </Typography>
      <Typography variant="body1" paragraph>
        Browse past sentiment analyses.
      </Typography>

      <FormControl sx={{ minWidth: 200, mb: 3 }}>
        <InputLabel>Filter by Mood</InputLabel>
        <Select
          value={selectedMoodId}
          label="Filter by Mood"
          onChange={(e) => setSelectedMoodId(e.target.value)}
        >
          <MenuItem value="">All Moods</MenuItem>
          {moods?.map((mood) => (
            <MenuItem key={mood.id} value={mood.id}>
              {mood.name}
            </MenuItem>
          ))}
        </Select>
      </FormControl>

      {isLoading ? (
        <Box display="flex" justifyContent="center" p={4}>
          <CircularProgress />
        </Box>
      ) : analyses && analyses.length > 0 ? (
        <TableContainer component={Paper}>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Date</TableCell>
                <TableCell>Mood</TableCell>
                <TableCell>Text</TableCell>
                <TableCell>Score</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {analyses.map((analysis) => (
                <TableRow key={analysis.id}>
                  <TableCell>
                    {new Date(analysis.analyzed_at).toLocaleString()}
                  </TableCell>
                  <TableCell>{getMoodName(analysis.mood_id)}</TableCell>
                  <TableCell>
                    {analysis.input_text.length > 100
                      ? analysis.input_text.substring(0, 100) + '...'
                      : analysis.input_text}
                  </TableCell>
                  <TableCell>
                    <Chip
                      label={analysis.score.toFixed(3)}
                      color={getScoreColor(analysis.score)}
                      size="small"
                    />
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      ) : (
        <Alert severity="info">No analyses found.</Alert>
      )}
    </Box>
  )
}
