import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import {
  Box,
  Typography,
  Button,
  Card,
  CardContent,
  CardActions,
  Grid,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  CircularProgress,
  Alert,
} from '@mui/material'
import { Add as AddIcon } from '@mui/icons-material'
import { Link } from 'react-router-dom'
import { moodsApi } from '@/services/api'
import type { MoodCreate } from '@/types'

export default function MoodsPage() {
  const queryClient = useQueryClient()
  const [dialogOpen, setDialogOpen] = useState(false)
  const [formData, setFormData] = useState<MoodCreate>({
    name: '',
    description: '',
    attribute_definition: '',
  })

  const { data: moods, isLoading, error } = useQuery({
    queryKey: ['moods'],
    queryFn: () => moodsApi.list().then((res) => res.data),
  })

  const createMutation = useMutation({
    mutationFn: (data: MoodCreate) => moodsApi.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['moods'] })
      setDialogOpen(false)
      setFormData({ name: '', description: '', attribute_definition: '' })
    },
  })

  const deleteMutation = useMutation({
    mutationFn: (id: string) => moodsApi.delete(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['moods'] })
    },
  })

  const handleSubmit = () => {
    createMutation.mutate(formData)
  }

  if (isLoading) {
    return (
      <Box display="flex" justifyContent="center" p={4}>
        <CircularProgress />
      </Box>
    )
  }

  if (error) {
    return <Alert severity="error">Failed to load moods</Alert>
  }

  return (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4">Moods</Typography>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={() => setDialogOpen(true)}
        >
          Create Mood
        </Button>
      </Box>

      {moods && moods.length === 0 ? (
        <Alert severity="info">
          No moods defined yet. Create your first mood to get started!
        </Alert>
      ) : (
        <Grid container spacing={3}>
          {moods?.map((mood) => (
            <Grid item xs={12} md={6} key={mood.id}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    {mood.name}
                  </Typography>
                  <Typography variant="body2" color="text.secondary" paragraph>
                    {mood.description}
                  </Typography>
                  <Typography variant="caption" color="text.secondary">
                    Created: {new Date(mood.created_at).toLocaleDateString()}
                  </Typography>
                </CardContent>
                <CardActions>
                  <Button component={Link} to={`/moods/${mood.id}`} size="small">
                    View Details
                  </Button>
                  <Button
                    size="small"
                    color="error"
                    onClick={() => deleteMutation.mutate(mood.id)}
                  >
                    Delete
                  </Button>
                </CardActions>
              </Card>
            </Grid>
          ))}
        </Grid>
      )}

      <Dialog open={dialogOpen} onClose={() => setDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Create New Mood</DialogTitle>
        <DialogContent>
          <TextField
            autoFocus
            margin="dense"
            label="Name"
            fullWidth
            value={formData.name}
            onChange={(e) => setFormData({ ...formData, name: e.target.value })}
          />
          <TextField
            margin="dense"
            label="Description"
            fullWidth
            multiline
            rows={2}
            value={formData.description}
            onChange={(e) => setFormData({ ...formData, description: e.target.value })}
          />
          <TextField
            margin="dense"
            label="Attribute Definition"
            fullWidth
            multiline
            rows={4}
            value={formData.attribute_definition}
            onChange={(e) =>
              setFormData({ ...formData, attribute_definition: e.target.value })
            }
            helperText="Define the semantic attribute to detect in text"
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDialogOpen(false)}>Cancel</Button>
          <Button
            onClick={handleSubmit}
            variant="contained"
            disabled={
              !formData.name || !formData.description || !formData.attribute_definition
            }
          >
            Create
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  )
}
