import { useState, useEffect } from 'react'
import { submissions } from '../api/client'
import { FileText, Image, Video, Link2, Calendar, Loader2 } from 'lucide-react'

export default function History() {
  const [submissionsList, setSubmissionsList] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    fetchSubmissions()
  }, [])

  const fetchSubmissions = async () => {
    try {
      const response = await submissions.getAll()
      setSubmissionsList(response.data)
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to load history')
    } finally {
      setLoading(false)
    }
  }

  const getContentIcon = (contentType) => {
    switch (contentType) {
      case 'text':
        return <FileText size={20} />
      case 'image':
        return <Image size={20} />
      case 'video':
        return <Video size={20} />
      case 'url':
        return <Link2 size={20} />
      default:
        return <FileText size={20} />
    }
  }

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  if (loading) {
    return (
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="flex justify-center items-center h-64">
          <Loader2 className="animate-spin text-primary-600" size={48} />
        </div>
      </div>
    )
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Detection History</h1>
        <p className="mt-2 text-gray-600">
          View all your previous AI detection analyses
        </p>
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-8 text-red-700">
          {error}
        </div>
      )}

      {submissionsList.length === 0 ? (
        <div className="card text-center py-12">
          <FileText className="mx-auto text-gray-400 mb-4" size={48} />
          <h3 className="text-lg font-medium text-gray-900 mb-2">No submissions yet</h3>
          <p className="text-gray-600 mb-6">
            Start analyzing content to see your detection history here.
          </p>
          <a href="/detect" className="btn-primary inline-block">
            Start Detection
          </a>
        </div>
      ) : (
        <div className="space-y-4">
          {submissionsList.map((submission) => (
            <div key={submission.id} className="card hover:shadow-lg transition-shadow">
              <div className="flex items-start justify-between">
                <div className="flex items-start space-x-4 flex-1">
                  <div className="p-3 bg-gray-100 rounded-lg">
                    {getContentIcon(submission.content_type)}
                  </div>
                  
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center space-x-2 mb-2">
                      <span className="px-2 py-1 text-xs font-medium bg-gray-100 text-gray-700 rounded capitalize">
                        {submission.content_type}
                      </span>
                      <span className="flex items-center text-sm text-gray-500">
                        <Calendar size={14} className="mr-1" />
                        {formatDate(submission.created_at)}
                      </span>
                    </div>
                    
                    <div className="text-sm text-gray-600 mb-3">
                      {submission.content_text && (
                        <p className="truncate">{submission.content_text.substring(0, 150)}...</p>
                      )}
                      {submission.content_url && (
                        <p className="truncate text-blue-600">{submission.content_url}</p>
                      )}
                    </div>
                    
                    {submission.detection_result && (
                      <div className="flex items-center space-x-4 text-sm">
                        <div>
                          <span className="text-gray-500">AI Confidence: </span>
                          <span className={`font-semibold ${
                            submission.detection_result.confidence_score >= 80 ? 'text-red-600' :
                            submission.detection_result.confidence_score >= 50 ? 'text-yellow-600' :
                            'text-green-600'
                          }`}>
                            {submission.detection_result.confidence_score.toFixed(1)}%
                          </span>
                        </div>
                        
                        {submission.detection_result.detected_model && (
                          <div>
                            <span className="text-gray-500">Model: </span>
                            <span className="font-semibold text-blue-600 capitalize">
                              {submission.detection_result.detected_model}
                            </span>
                          </div>
                        )}
                      </div>
                    )}
                  </div>
                </div>
                
                {submission.detection_result && (
                  <div className={`px-4 py-2 rounded-full ${
                    submission.detection_result.is_ai_generated
                      ? 'bg-red-100 text-red-700'
                      : 'bg-green-100 text-green-700'
                  }`}>
                    <span className="text-sm font-medium">
                      {submission.detection_result.is_ai_generated ? 'AI' : 'Human'}
                    </span>
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
