import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import {
  Box,
  Typography,
  Card,
  CardContent,
  CardActions,
  Grid,
  Switch,
  Button,
  Chip,
  Alert,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  CircularProgress,
  Accordion,
  AccordionSummary,
  AccordionDetails,
} from '@mui/material'
import {
  ExpandMore,
  CheckCircle,
  Error,
  Warning,
  Settings,
} from '@mui/icons-material'
import { featuresApi } from '@/services/api'

export default function FeaturesPage() {
  const queryClient = useQueryClient()
  const [selectedFeature, setSelectedFeature] = useState<any>(null)
  const [configDialogOpen, setConfigDialogOpen] = useState(false)
  const [config, setConfig] = useState<any>({})

  const { data: features, isLoading } = useQuery({
    queryKey: ['features'],
    queryFn: () => featuresApi.list().then((res) => res.data),
  })

  const enableMutation = useMutation({
    mutationFn: ({ name, config }: any) => featuresApi.enable(name, config),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['features'] })
      setConfigDialogOpen(false)
      setSelectedFeature(null)
    },
  })

  const disableMutation = useMutation({
    mutationFn: (name: string) => featuresApi.disable(name),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['features'] })
    },
  })

  const handleToggle = (feature: any) => {
    if (feature.enabled) {
      // Disable
      if (confirm(`Disable ${feature.display_name}?`)) {
        disableMutation.mutate(feature.name)
      }
    } else {
      // Enable - show config dialog
      setSelectedFeature(feature)
      setConfig({})
      setConfigDialogOpen(true)
    }
  }

  const handleEnableWithConfig = () => {
    if (!selectedFeature) return
    enableMutation.mutate({
      name: selectedFeature.name,
      config,
    })
  }

  const getCategoryColor = (category: string) => {
    const colors: any = {
      monitoring: 'primary',
      notifications: 'secondary',
      storage: 'success',
      compliance: 'warning',
    }
    return colors[category] || 'default'
  }

  const getDependencyStatus = (feature: any) => {
    if (!feature.dependencies_met) return null

    const allMet = Object.values(feature.dependencies_met).every((v) => v === true)
    const missing = Object.entries(feature.dependencies_met)
      .filter(([_, met]) => !met)
      .map(([dep]) => dep)

    return {
      allMet,
      missing,
      count: Object.keys(feature.dependencies_met).length,
    }
  }

  if (isLoading) {
    return (
      <Box display="flex" justifyContent="center" p={4}>
        <CircularProgress />
      </Box>
    )
  }

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Feature Management
      </Typography>
      <Typography variant="body1" paragraph>
        Enable and configure optional integrations. Features are disabled by default and only
        activate when explicitly enabled.
      </Typography>

      <Alert severity="info" sx={{ mb: 3 }}>
        <strong>Optional Features:</strong> All features below are optional and won't affect
        existing functionality. Dependencies must be installed before enabling.
      </Alert>

      <Grid container spacing={3}>
        {features?.map((feature: any) => {
          const depStatus = getDependencyStatus(feature)

          return (
            <Grid item xs={12} md={6} key={feature.id}>
              <Card>
                <CardContent>
                  <Box display="flex" justifyContent="space-between" alignItems="start" mb={2}>
                    <Box>
                      <Typography variant="h6">{feature.display_name}</Typography>
                      <Chip
                        label={feature.category}
                        color={getCategoryColor(feature.category)}
                        size="small"
                        sx={{ mt: 1 }}
                      />
                    </Box>
                    <Switch
                      checked={feature.enabled}
                      onChange={() => handleToggle(feature)}
                      color="primary"
                      disabled={
                        !feature.enabled && depStatus && !depStatus.allMet
                      }
                    />
                  </Box>

                  <Typography variant="body2" color="text.secondary" paragraph>
                    {feature.description}
                  </Typography>

                  {/* Dependency Status */}
                  {depStatus && depStatus.count > 0 && (
                    <Box mt={2}>
                      <Typography variant="caption" display="block" gutterBottom>
                        Dependencies:
                      </Typography>
                      {depStatus.allMet ? (
                        <Chip
                          icon={<CheckCircle />}
                          label="All dependencies met"
                          color="success"
                          size="small"
                        />
                      ) : (
                        <Box>
                          <Chip
                            icon={<Error />}
                            label={`${depStatus.missing.length} missing`}
                            color="error"
                            size="small"
                          />
                          <Typography variant="caption" display="block" sx={{ mt: 1 }}>
                            Missing: {depStatus.missing.join(', ')}
                          </Typography>
                          <Typography variant="caption" display="block" color="error">
                            Install with: pip install {depStatus.missing.join(' ')}
                          </Typography>
                        </Box>
                      )}
                    </Box>
                  )}

                  {/* Current Status */}
                  {feature.enabled && (
                    <Accordion sx={{ mt: 2 }}>
                      <AccordionSummary expandIcon={<ExpandMore />}>
                        <Typography variant="caption">
                          <Settings fontSize="small" sx={{ mr: 1, verticalAlign: 'middle' }} />
                          Configuration
                        </Typography>
                      </AccordionSummary>
                      <AccordionDetails>
                        <Box>
                          {Object.entries(feature.config).map(([key, value]: any) => (
                            <Typography variant="caption" display="block" key={key}>
                              <strong>{key}:</strong> {key.includes('password') || key.includes('secret') ? '••••••••' : String(value)}
                            </Typography>
                          ))}
                          {feature.enabled_at && (
                            <Typography variant="caption" display="block" color="text.secondary" sx={{ mt: 1 }}>
                              Enabled: {new Date(feature.enabled_at).toLocaleString()}
                            </Typography>
                          )}
                        </Box>
                      </AccordionDetails>
                    </Accordion>
                  )}
                </CardContent>
              </Card>
            </Grid>
          )
        })}
      </Grid>

      {/* Configuration Dialog */}
      <Dialog
        open={configDialogOpen}
        onClose={() => setConfigDialogOpen(false)}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>
          Enable {selectedFeature?.display_name}
        </DialogTitle>
        <DialogContent>
          <Alert severity="warning" sx={{ mb: 2 }}>
            This feature requires configuration. Enter the required values below.
          </Alert>

          <Typography variant="body2" paragraph>
            {selectedFeature?.description}
          </Typography>

          <Box component="form" sx={{ mt: 2 }}>
            {selectedFeature?.name === 'sentry' && (
              <>
                <TextField
                  fullWidth
                  label="Sentry DSN"
                  margin="normal"
                  required
                  helperText="Your Sentry project DSN (https://xxx@sentry.io/xxx)"
                  onChange={(e) => setConfig({ ...config, dsn: e.target.value })}
                />
                <TextField
                  fullWidth
                  label="Environment"
                  margin="normal"
                  defaultValue="production"
                  onChange={(e) => setConfig({ ...config, environment: e.target.value })}
                />
              </>
            )}

            {selectedFeature?.name === 'email_notifications' && (
              <>
                <TextField
                  fullWidth
                  label="SMTP Host"
                  margin="normal"
                  required
                  onChange={(e) => setConfig({ ...config, smtp_host: e.target.value })}
                />
                <TextField
                  fullWidth
                  label="SMTP Port"
                  margin="normal"
                  type="number"
                  defaultValue={587}
                  onChange={(e) => setConfig({ ...config, smtp_port: parseInt(e.target.value) })}
                />
                <TextField
                  fullWidth
                  label="SMTP User"
                  margin="normal"
                  required
                  onChange={(e) => setConfig({ ...config, smtp_user: e.target.value })}
                />
                <TextField
                  fullWidth
                  label="SMTP Password"
                  margin="normal"
                  type="password"
                  required
                  onChange={(e) => setConfig({ ...config, smtp_password: e.target.value })}
                />
                <TextField
                  fullWidth
                  label="From Email"
                  margin="normal"
                  required
                  onChange={(e) => setConfig({ ...config, from_email: e.target.value })}
                />
              </>
            )}

            {selectedFeature?.name === 'webhooks' && (
              <>
                <TextField
                  fullWidth
                  label="Webhook URL"
                  margin="normal"
                  required
                  helperText="HTTPS endpoint to receive webhook notifications"
                  onChange={(e) => setConfig({ ...config, webhook_url: e.target.value })}
                />
                <TextField
                  fullWidth
                  label="Secret (optional)"
                  margin="normal"
                  type="password"
                  helperText="For HMAC signature verification"
                  onChange={(e) => setConfig({ ...config, secret: e.target.value })}
                />
              </>
            )}
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setConfigDialogOpen(false)}>
            Cancel
          </Button>
          <Button
            onClick={handleEnableWithConfig}
            variant="contained"
            disabled={enableMutation.isPending}
          >
            {enableMutation.isPending ? 'Enabling...' : 'Enable Feature'}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  )
}
