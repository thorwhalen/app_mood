import { useState } from 'react'
import { useParams } from 'react-router-dom'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import {
  Box,
  Typography,
  Button,
  Card,
  CardContent,
  Tabs,
  Tab,
  CircularProgress,
  Alert,
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableRow,
  Chip,
} from '@mui/material'
import { moodsApi, datasetsApi, modelsApi } from '@/services/api'

interface TabPanelProps {
  children?: React.ReactNode
  index: number
  value: number
}

function TabPanel(props: TabPanelProps) {
  const { children, value, index, ...other } = props
  return (
    <div hidden={value !== index} {...other}>
      {value === index && <Box sx={{ p: 3 }}>{children}</Box>}
    </div>
  )
}

export default function MoodDetailPage() {
  const { id } = useParams<{ id: string }>()
  const queryClient = useQueryClient()
  const [tabValue, setTabValue] = useState(0)

  const { data: mood, isLoading: moodLoading } = useQuery({
    queryKey: ['mood', id],
    queryFn: () => moodsApi.get(id!).then((res) => res.data),
    enabled: !!id,
  })

  const { data: datasets } = useQuery({
    queryKey: ['datasets', id],
    queryFn: () => datasetsApi.listByMood(id!).then((res) => res.data),
    enabled: !!id,
  })

  const { data: models } = useQuery({
    queryKey: ['models', id],
    queryFn: () => modelsApi.listByMood(id!).then((res) => res.data),
    enabled: !!id,
  })

  const generateDatasetMutation = useMutation({
    mutationFn: () =>
      datasetsApi.generate(id!, { num_examples: 20, openai_model: 'gpt-4' }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['datasets', id] })
    },
  })

  const trainModelMutation = useMutation({
    mutationFn: (datasetId: string) => modelsApi.train(id!, datasetId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['models', id] })
    },
  })

  if (moodLoading) {
    return (
      <Box display="flex" justifyContent="center" p={4}>
        <CircularProgress />
      </Box>
    )
  }

  if (!mood) {
    return <Alert severity="error">Mood not found</Alert>
  }

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        {mood.name}
      </Typography>
      <Typography variant="body1" paragraph>
        {mood.description}
      </Typography>

      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Typography variant="subtitle2" color="text.secondary" gutterBottom>
            Attribute Definition
          </Typography>
          <Typography variant="body2">{mood.attribute_definition}</Typography>
        </CardContent>
      </Card>

      <Tabs value={tabValue} onChange={(_, newValue) => setTabValue(newValue)}>
        <Tab label="Datasets" />
        <Tab label="Models" />
      </Tabs>

      <TabPanel value={tabValue} index={0}>
        <Box display="flex" justifyContent="space-between" mb={2}>
          <Typography variant="h6">Training Datasets</Typography>
          <Button
            variant="contained"
            onClick={() => generateDatasetMutation.mutate()}
            disabled={generateDatasetMutation.isPending}
          >
            Generate Dataset
          </Button>
        </Box>

        {datasets && datasets.length > 0 ? (
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Generated At</TableCell>
                <TableCell>Examples</TableCell>
                <TableCell>Status</TableCell>
                <TableCell>Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {datasets.map((dataset) => (
                <TableRow key={dataset.id}>
                  <TableCell>
                    {new Date(dataset.generated_at).toLocaleString()}
                  </TableCell>
                  <TableCell>{dataset.num_examples}</TableCell>
                  <TableCell>
                    <Chip label={dataset.status} size="small" />
                  </TableCell>
                  <TableCell>
                    {dataset.status === 'completed' && (
                      <Button
                        size="small"
                        onClick={() => trainModelMutation.mutate(dataset.id)}
                      >
                        Train Models
                      </Button>
                    )}
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        ) : (
          <Alert severity="info">No datasets yet. Generate one to get started!</Alert>
        )}
      </TabPanel>

      <TabPanel value={tabValue} index={1}>
        <Typography variant="h6" gutterBottom>
          Trained Models
        </Typography>

        {models && models.length > 0 ? (
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Model Type</TableCell>
                <TableCell>Metrics</TableCell>
                <TableCell>Trained At</TableCell>
                <TableCell>Selected</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {models.map((model) => (
                <TableRow key={model.id}>
                  <TableCell>{model.model_type}</TableCell>
                  <TableCell>
                    {model.metrics
                      ? Object.entries(model.metrics)
                          .map(([k, v]) => `${k}: ${v.toFixed(3)}`)
                          .join(', ')
                      : 'N/A'}
                  </TableCell>
                  <TableCell>
                    {new Date(model.trained_at).toLocaleString()}
                  </TableCell>
                  <TableCell>
                    {model.is_selected ? (
                      <Chip label="Selected" color="primary" size="small" />
                    ) : (
                      <Button
                        size="small"
                        onClick={() => modelsApi.select(model.id)}
                      >
                        Select
                      </Button>
                    )}
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        ) : (
          <Alert severity="info">
            No models trained yet. Generate a dataset and train models!
          </Alert>
        )}
      </TabPanel>
    </Box>
  )
}
