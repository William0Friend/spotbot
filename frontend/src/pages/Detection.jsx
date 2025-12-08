import { useState } from 'react'
import { detection } from '../api/client'
import { FileText, Image, Video, Link2, AlertCircle, CheckCircle, Loader2 } from 'lucide-react'

/**
 * Detection Page Component
 * 
 * Main detection interface where users submit content for AI analysis.
 * 
 * Features:
 * - Multi-format support: text, image URLs, video URLs, web URLs
 * - Real-time analysis with loading states
 * - Color-coded confidence visualization
 * - Detailed results breakdown
 * 
 * User flow:
 * 1. Select content type (text/image/video/url)
 * 2. Paste/enter content
 * 3. Click "Analyze Content"
 * 4. See confidence scores + detected model
 * 5. View detailed analysis breakdown
 * 
 * State management:
 * - contentType: Which input field to show (text vs url)
 * - contentText/contentUrl: User input
 * - loading: Disable form during API call
 * - result: Detection response from backend
 * - error: Display API errors to user
 * 
 * Why this design:
 * - Single-page interface: Fast, no navigation needed
 * - Instant feedback: Loading spinner, immediate results
 * - Progressive disclosure: Basic result → detailed breakdown on expand
 * 
 * @component
 */
export default function Detection() {
  // Content input state
  const [contentType, setContentType] = useState('text')  // text|image|video|url
  const [contentText, setContentText] = useState('')      // For direct text input
  const [contentUrl, setContentUrl] = useState('')        // For URL-based content
  
  // UI state
  const [loading, setLoading] = useState(false)   // Show spinner during analysis
  const [result, setResult] = useState(null)      // Detection result from API
  const [error, setError] = useState(null)        // Error message if API fails

  /**
   * Handle form submission and call detection API
   * 
   * Validates input, calls backend, handles success/error states
   * 
   * @param {Event} e - Form submit event
   */
  const handleAnalyze = async (e) => {
    e.preventDefault()
    setLoading(true)
    setError(null)
    setResult(null)

    try {
      const requestData = {
        content_type: contentType,
        content_text: contentType === 'text' ? contentText : null,
        content_url: contentType !== 'text' ? contentUrl : null,
      }

      const response = await detection.analyze(requestData)
      setResult(response.data)
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to analyze content')
    } finally {
      setLoading(false)
    }
  }

  /**
   * Get color for confidence score display (text color)
   * 
   * Visual feedback helps users quickly assess confidence level:
   * - Red (< 40%): Low confidence, likely human
   * - Yellow (40-60%): Moderate, uncertain
   * - Orange (60-80%): High, probably AI
   * - Green (≥ 80%): Very high, almost certainly AI
   * 
   * @param {number} score - Confidence score (0-100)
   * @returns {string} Tailwind text color class
   */
  const getConfidenceColor = (score) => {
    if (score >= 80) return 'text-red-600'
    if (score >= 50) return 'text-yellow-600'
    return 'text-green-600'
  }

  /**
   * Get background color for confidence badge
   * 
   * Matches getConfidenceColor but for badge backgrounds
   * 
   * @param {number} score - Confidence score (0-100)
   * @returns {string} Tailwind background color class
   */
  const getConfidenceBgColor = (score) => {
    if (score >= 80) return 'bg-red-100'
    if (score >= 50) return 'bg-yellow-100'
    return 'bg-green-100'
  }

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      <div className="text-center mb-8">
        <h1 className="text-3xl font-bold text-gray-900">AI Content Detection</h1>
        <p className="mt-2 text-gray-600">
          Upload or paste content to analyze for AI generation
        </p>
      </div>

      <div className="card mb-8">
        {/* Content Type Selector */}
        <div className="mb-6">
          <label className="block text-sm font-medium text-gray-700 mb-3">
            Content Type
          </label>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
            <button
              onClick={() => setContentType('text')}
              className={`p-4 border-2 rounded-lg flex flex-col items-center justify-center space-y-2 transition-all ${
                contentType === 'text'
                  ? 'border-primary-600 bg-primary-50'
                  : 'border-gray-200 hover:border-gray-300'
              }`}
            >
              <FileText size={24} />
              <span className="text-sm font-medium">Text</span>
            </button>

            <button
              onClick={() => setContentType('image')}
              className={`p-4 border-2 rounded-lg flex flex-col items-center justify-center space-y-2 transition-all ${
                contentType === 'image'
                  ? 'border-primary-600 bg-primary-50'
                  : 'border-gray-200 hover:border-gray-300'
              }`}
            >
              <Image size={24} />
              <span className="text-sm font-medium">Image</span>
            </button>

            <button
              onClick={() => setContentType('video')}
              className={`p-4 border-2 rounded-lg flex flex-col items-center justify-center space-y-2 transition-all ${
                contentType === 'video'
                  ? 'border-primary-600 bg-primary-50'
                  : 'border-gray-200 hover:border-gray-300'
              }`}
            >
              <Video size={24} />
              <span className="text-sm font-medium">Video</span>
            </button>

            <button
              onClick={() => setContentType('url')}
              className={`p-4 border-2 rounded-lg flex flex-col items-center justify-center space-y-2 transition-all ${
                contentType === 'url'
                  ? 'border-primary-600 bg-primary-50'
                  : 'border-gray-200 hover:border-gray-300'
              }`}
            >
              <Link2 size={24} />
              <span className="text-sm font-medium">URL</span>
            </button>
          </div>
        </div>

        {/* Input Form */}
        <form onSubmit={handleAnalyze}>
          {contentType === 'text' ? (
            <div className="mb-6">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Text Content
              </label>
              <textarea
                value={contentText}
                onChange={(e) => setContentText(e.target.value)}
                rows={8}
                className="input"
                placeholder="Paste or type text to analyze..."
                required
              />
            </div>
          ) : (
            <div className="mb-6">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                {contentType === 'image' && 'Image URL'}
                {contentType === 'video' && 'Video URL'}
                {contentType === 'url' && 'Web URL'}
              </label>
              <input
                type="url"
                value={contentUrl}
                onChange={(e) => setContentUrl(e.target.value)}
                className="input"
                placeholder={`https://example.com/${contentType}`}
                required
              />
            </div>
          )}

          <button
            type="submit"
            disabled={loading}
            className="btn-primary w-full flex items-center justify-center"
          >
            {loading ? (
              <>
                <Loader2 className="animate-spin mr-2" size={20} />
                Analyzing...
              </>
            ) : (
              'Analyze Content'
            )}
          </button>
        </form>
      </div>

      {/* Error Display */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-8 flex items-start">
          <AlertCircle className="text-red-600 mr-3 flex-shrink-0" size={24} />
          <div>
            <h3 className="text-red-800 font-medium">Analysis Failed</h3>
            <p className="text-red-700 text-sm mt-1">{error}</p>
          </div>
        </div>
      )}

      {/* Results Display */}
      {result && (
        <div className="card">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-2xl font-bold text-gray-900">Analysis Results</h2>
            <div className={`px-4 py-2 rounded-full ${getConfidenceBgColor(result.confidence_score)}`}>
              <span className={`font-semibold ${getConfidenceColor(result.confidence_score)}`}>
                {result.confidence_score.toFixed(1)}% Confidence
              </span>
            </div>
          </div>

          {/* AI Detection Status */}
          <div className="mb-6 p-4 bg-gray-50 rounded-lg">
            <div className="flex items-center">
              {result.is_ai_generated ? (
                <>
                  <AlertCircle className="text-red-600 mr-3" size={24} />
                  <div>
                    <h3 className="font-semibold text-gray-900">AI-Generated Content Detected</h3>
                    <p className="text-gray-600 text-sm">
                      This content appears to be generated by artificial intelligence.
                    </p>
                  </div>
                </>
              ) : (
                <>
                  <CheckCircle className="text-green-600 mr-3" size={24} />
                  <div>
                    <h3 className="font-semibold text-gray-900">Likely Human-Generated</h3>
                    <p className="text-gray-600 text-sm">
                      This content does not show strong signs of AI generation.
                    </p>
                  </div>
                </>
              )}
            </div>
          </div>

          {/* Model Detection */}
          {result.detected_model && (
            <div className="mb-6">
              <h3 className="font-semibold text-gray-900 mb-2">Detected Model</h3>
              <div className="flex items-center justify-between p-3 bg-blue-50 rounded-lg">
                <span className="text-blue-900 font-medium capitalize">
                  {result.detected_model}
                </span>
                {result.model_confidence && (
                  <span className="text-blue-700 text-sm">
                    {result.model_confidence.toFixed(1)}% confidence
                  </span>
                )}
              </div>
            </div>
          )}

          {/* Analysis Details */}
          {result.analysis_details && (
            <div>
              <h3 className="font-semibold text-gray-900 mb-2">Analysis Details</h3>
              <div className="bg-gray-50 rounded-lg p-4">
                <pre className="text-sm text-gray-700 overflow-x-auto">
                  {JSON.stringify(result.analysis_details, null, 2)}
                </pre>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  )
}
