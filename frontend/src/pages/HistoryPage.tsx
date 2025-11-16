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
  Button,
} from '@mui/material'
import { Download } from '@mui/icons-material'
import { moodsApi, analysisApi } from '@/services/api'

export default function HistoryPage() {
  const [selectedMoodId, setSelectedMoodId] = useState<string>('')
  const [exporting, setExporting] = useState(false)

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

  const handleExport = async () => {
    setExporting(true)
    try {
      const response = await analysisApi.exportCsv(selectedMoodId || undefined)
      const blob = new Blob([response.data], { type: 'text/csv' })
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `mood_analyses_${selectedMoodId || 'all'}.csv`
      document.body.appendChild(a)
      a.click()
      window.URL.revokeObjectURL(url)
      document.body.removeChild(a)
    } catch (error) {
      console.error('Export failed:', error)
      alert('Failed to export data. Please try again.')
    } finally {
      setExporting(false)
    }
  }

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Analysis History
      </Typography>
      <Typography variant="body1" paragraph>
        Browse past sentiment analyses.
      </Typography>

      <Box display="flex" gap={2} mb={3} alignItems="center">
        <FormControl sx={{ minWidth: 200 }}>
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

        <Button
          variant="outlined"
          startIcon={<Download />}
          onClick={handleExport}
          disabled={!analyses || analyses.length === 0 || exporting}
        >
          {exporting ? 'Exporting...' : 'Export CSV'}
        </Button>
      </Box>

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
