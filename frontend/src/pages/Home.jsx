import { Link } from 'react-router-dom'
import { Search, Shield, Zap, BarChart, ArrowRight } from 'lucide-react'

/**
 * Home Page / Landing Page Component
 * 
 * Marketing page that introduces SpotBot and drives users to detection tool.
 * 
 * Structure:
 * - Hero section: Value proposition + CTA buttons
 * - Features section: 4 key features with icons
 * - How it works: 3-step process explanation
 * - CTA section: Final push to start detection
 * 
 * Design goals:
 * - Clear value proposition in first 3 seconds
 * - Multiple CTAs to reduce friction
 * - Social proof ready (stats, testimonials)
 * - Mobile-responsive layout
 * 
 * User flows:
 * 1. Anonymous user → Start Detection (no login required)
 * 2. Developer → API Docs (integration guide)
 * 3. Interested user → Learn more → Features
 * 
 * @component
 */
export default function Home() {
  return (
    <div className="bg-white">
      {/* Hero Section */}
      <div className="relative overflow-hidden">
        <div className="max-w-7xl mx-auto">
          <div className="relative z-10 pb-8 sm:pb-16 md:pb-20 lg:w-full lg:pb-28 xl:pb-32">
            <main className="mt-10 mx-auto max-w-7xl px-4 sm:mt-12 sm:px-6 md:mt-16 lg:mt-20 lg:px-8 xl:mt-28">
              <div className="text-center">
                <h1 className="text-4xl tracking-tight font-extrabold text-gray-900 sm:text-5xl md:text-6xl">
                  <span className="block">Detect AI-Generated</span>
                  <span className="block text-primary-600">Content with Confidence</span>
                </h1>
                <p className="mt-3 max-w-md mx-auto text-base text-gray-500 sm:text-lg md:mt-5 md:text-xl md:max-w-3xl">
                  Upload text, images, videos, or URLs and get instant AI detection results. 
                  Identify which LLM created the content with detailed confidence scores.
                </p>
                <div className="mt-5 max-w-md mx-auto sm:flex sm:justify-center md:mt-8">
                  <div className="rounded-md shadow">
                    <Link
                      to="/detect"
                      className="w-full flex items-center justify-center px-8 py-3 border border-transparent text-base font-medium rounded-md text-white bg-primary-600 hover:bg-primary-700 md:py-4 md:text-lg md:px-10"
                    >
                      Start Detection
                      <ArrowRight className="ml-2" size={20} />
                    </Link>
                  </div>
                  <div className="mt-3 rounded-md shadow sm:mt-0 sm:ml-3">
                    <a
                      href="http://localhost:8000/docs"
                      className="w-full flex items-center justify-center px-8 py-3 border border-transparent text-base font-medium rounded-md text-primary-600 bg-white hover:bg-gray-50 md:py-4 md:text-lg md:px-10"
                    >
                      API Docs
                    </a>
                  </div>
                </div>
              </div>
            </main>
          </div>
        </div>
      </div>

      {/* Features Section */}
      <div className="py-12 bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center">
            <h2 className="text-3xl font-extrabold text-gray-900">
              Powerful AI Detection Features
            </h2>
            <p className="mt-4 text-lg text-gray-500">
              Everything you need to identify AI-generated content
            </p>
          </div>

          <div className="mt-10">
            <div className="grid grid-cols-1 gap-10 sm:grid-cols-2 lg:grid-cols-4">
              <div className="text-center">
                <div className="flex items-center justify-center h-12 w-12 rounded-md bg-primary-600 text-white mx-auto">
                  <Search size={24} />
                </div>
                <h3 className="mt-5 text-lg font-medium text-gray-900">Multi-Format Detection</h3>
                <p className="mt-2 text-base text-gray-500">
                  Analyze text, images, videos, and URLs
                </p>
              </div>

              <div className="text-center">
                <div className="flex items-center justify-center h-12 w-12 rounded-md bg-primary-600 text-white mx-auto">
                  <Shield size={24} />
                </div>
                <h3 className="mt-5 text-lg font-medium text-gray-900">Model Identification</h3>
                <p className="mt-2 text-base text-gray-500">
                  Identify GPT, Claude, Gemini, and more
                </p>
              </div>

              <div className="text-center">
                <div className="flex items-center justify-center h-12 w-12 rounded-md bg-primary-600 text-white mx-auto">
                  <BarChart size={24} />
                </div>
                <h3 className="mt-5 text-lg font-medium text-gray-900">Confidence Scores</h3>
                <p className="mt-2 text-base text-gray-500">
                  Get detailed 0-100% confidence ratings
                </p>
              </div>

              <div className="text-center">
                <div className="flex items-center justify-center h-12 w-12 rounded-md bg-primary-600 text-white mx-auto">
                  <Zap size={24} />
                </div>
                <h3 className="mt-5 text-lg font-medium text-gray-900">Instant Results</h3>
                <p className="mt-2 text-base text-gray-500">
                  Fast analysis with real-time feedback
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Use Cases Section */}
      <div className="py-12 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-extrabold text-gray-900">
              Use Cases
            </h2>
          </div>

          <div className="grid grid-cols-1 gap-8 md:grid-cols-3">
            <div className="card">
              <h3 className="text-xl font-semibold mb-3">Content Moderation</h3>
              <p className="text-gray-600">
                Identify AI-generated content in user submissions, comments, and posts across your platform.
              </p>
            </div>

            <div className="card">
              <h3 className="text-xl font-semibold mb-3">Academic Integrity</h3>
              <p className="text-gray-600">
                Detect AI-written essays, papers, and assignments to maintain educational standards.
              </p>
            </div>

            <div className="card">
              <h3 className="text-xl font-semibold mb-3">Bot Detection</h3>
              <p className="text-gray-600">
                Identify bot accounts and automated content generation across social media platforms.
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* CTA Section */}
      <div className="bg-primary-600">
        <div className="max-w-7xl mx-auto py-12 px-4 sm:px-6 lg:py-16 lg:px-8 lg:flex lg:items-center lg:justify-between">
          <h2 className="text-3xl font-extrabold tracking-tight text-white sm:text-4xl">
            <span className="block">Ready to get started?</span>
            <span className="block text-primary-200">Try SpotBot today.</span>
          </h2>
          <div className="mt-8 flex lg:mt-0 lg:flex-shrink-0">
            <div className="inline-flex rounded-md shadow">
              <Link
                to="/detect"
                className="inline-flex items-center justify-center px-5 py-3 border border-transparent text-base font-medium rounded-md text-primary-600 bg-white hover:bg-gray-50"
              >
                Start Detection
              </Link>
            </div>
            <div className="ml-3 inline-flex rounded-md shadow">
              <Link
                to="/register"
                className="inline-flex items-center justify-center px-5 py-3 border border-transparent text-base font-medium rounded-md text-white bg-primary-700 hover:bg-primary-800"
              >
                Sign Up Free
              </Link>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
