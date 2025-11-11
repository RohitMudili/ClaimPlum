import { formatCurrency } from '../utils/helpers';

const SalesConversion = ({ salesData }) => {
  const { sales_pitch, claim_preview, policy_benefits, next_steps, contact_info } = salesData;

  return (
    <div className="max-w-4xl mx-auto p-6">
      <div className="bg-gradient-to-br from-purple-50 to-pink-50 rounded-xl shadow-2xl overflow-hidden">
        {/* Hero Section */}
        <div className="p-8 bg-gradient-to-r from-purple-600 to-pink-600 text-white">
          <div className="text-center space-y-4">
            <div className="text-6xl mb-4">💼</div>
            <h1 className="text-4xl font-bold">{sales_pitch?.headline || 'Join Plum Today!'}</h1>
            <p className="text-xl text-purple-100">{salesData.message}</p>
          </div>
        </div>

        {/* Value Proposition */}
        <div className="p-8 bg-white border-b-4 border-purple-500">
          <div className="text-center space-y-4">
            <h2 className="text-2xl font-bold text-gray-900">Here's What You Would Have Saved</h2>
            <div className="bg-gradient-to-r from-purple-100 to-pink-100 p-6 rounded-xl">
              <p className="text-xl text-gray-800 font-medium">
                {sales_pitch?.value_proposition}
              </p>
            </div>
          </div>
        </div>

        {/* Claim Preview - What We Found */}
        {claim_preview && (
          <div className="p-8 border-b border-gray-200">
            <h3 className="text-2xl font-semibold text-gray-900 mb-6 text-center">
              We Analyzed Your Claim
            </h3>

            {/* Amount Breakdown */}
            <div className="grid md:grid-cols-3 gap-6 mb-6">
              <div className="bg-white p-6 rounded-lg shadow-md border-2 border-gray-200">
                <div className="text-sm text-gray-600 mb-2">Your Claim Amount</div>
                <div className="text-3xl font-bold text-gray-900">
                  {formatCurrency(claim_preview.your_claim_amount)}
                </div>
              </div>
              <div className="bg-gradient-to-br from-green-50 to-emerald-50 p-6 rounded-lg shadow-md border-2 border-green-300">
                <div className="text-sm text-green-700 mb-2">Plum Would Cover</div>
                <div className="text-3xl font-bold text-green-600">
                  {formatCurrency(claim_preview.plum_would_cover)}
                </div>
                <div className="text-sm text-green-600 mt-1">
                  {claim_preview.coverage_percentage}% coverage
                </div>
              </div>
              <div className="bg-gradient-to-br from-purple-50 to-pink-50 p-6 rounded-lg shadow-md border-2 border-purple-300">
                <div className="text-sm text-purple-700 mb-2">Your Savings</div>
                <div className="text-3xl font-bold text-purple-600">
                  {formatCurrency(claim_preview.your_savings)}
                </div>
              </div>
            </div>

            {/* What We Found */}
            {claim_preview.what_we_found && (
              <div className="bg-blue-50 p-6 rounded-lg">
                <h4 className="font-semibold text-gray-900 mb-3">What We Found in Your Documents:</h4>
                <div className="space-y-2">
                  {claim_preview.what_we_found.diagnosis && (
                    <div className="flex items-start space-x-3">
                      <span className="text-blue-600">🏥</span>
                      <div>
                        <span className="text-sm text-gray-600">Diagnosis:</span>
                        <span className="ml-2 text-gray-900 font-medium">{claim_preview.what_we_found.diagnosis}</span>
                      </div>
                    </div>
                  )}
                  {claim_preview.what_we_found.doctor && (
                    <div className="flex items-start space-x-3">
                      <span className="text-blue-600">👨‍⚕️</span>
                      <div>
                        <span className="text-sm text-gray-600">Doctor:</span>
                        <span className="ml-2 text-gray-900 font-medium">{claim_preview.what_we_found.doctor}</span>
                      </div>
                    </div>
                  )}
                  {claim_preview.what_we_found.hospital && (
                    <div className="flex items-start space-x-3">
                      <span className="text-blue-600">🏢</span>
                      <div>
                        <span className="text-sm text-gray-600">Hospital:</span>
                        <span className="ml-2 text-gray-900 font-medium">{claim_preview.what_we_found.hospital}</span>
                      </div>
                    </div>
                  )}
                </div>
              </div>
            )}

            {/* Copay Details */}
            {claim_preview.copay_details && (
              <div className="mt-4 bg-yellow-50 p-4 rounded-lg border border-yellow-200">
                <h4 className="font-semibold text-gray-900 mb-2">How It Works:</h4>
                <div className="space-y-1 text-sm">
                  <div className="flex items-center space-x-2">
                    <span className="text-yellow-600">✓</span>
                    <span className="text-gray-700">{claim_preview.copay_details.consultation}</span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <span className="text-yellow-600">✓</span>
                    <span className="text-gray-700">{claim_preview.copay_details.network_discount}</span>
                  </div>
                </div>
              </div>
            )}
          </div>
        )}

        {/* Policy Benefits */}
        {policy_benefits && (
          <div className="p-8 bg-gradient-to-br from-green-50 to-emerald-50 border-b border-gray-200">
            <h3 className="text-2xl font-semibold text-gray-900 mb-6 text-center">
              Why Companies Choose Plum
            </h3>
            <div className="grid md:grid-cols-2 gap-4">
              {Object.entries(policy_benefits).map(([key, value]) => (
                <div key={key} className="bg-white p-4 rounded-lg shadow-sm flex items-start space-x-3">
                  <span className="text-green-600 text-2xl">✓</span>
                  <div>
                    <div className="font-semibold text-gray-900 capitalize">
                      {key.replace(/_/g, ' ')}
                    </div>
                    <div className="text-gray-700">{value}</div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* CTA Section */}
        <div className="p-8 bg-gradient-to-r from-purple-600 to-pink-600 text-white text-center">
          <h3 className="text-3xl font-bold mb-4">{sales_pitch?.cta || 'Get Started Today'}</h3>
          <p className="text-purple-100 mb-6">{sales_pitch?.urgency}</p>
          <a
            href={sales_pitch?.cta_url || 'https://plumhq.com/get-quote'}
            target="_blank"
            rel="noopener noreferrer"
            className="inline-block bg-white text-purple-600 px-8 py-4 rounded-lg font-bold text-lg hover:bg-purple-50 transition-colors shadow-lg hover:shadow-xl transform hover:scale-105"
          >
            Get Free Quote →
          </a>
        </div>

        {/* Next Steps */}
        {next_steps && next_steps.length > 0 && (
          <div className="p-8 border-t border-gray-200">
            <h3 className="text-xl font-semibold text-gray-900 mb-4">Next Steps:</h3>
            <ol className="space-y-3">
              {next_steps.map((step, index) => (
                <li key={index} className="flex items-start space-x-3">
                  <span className="flex-shrink-0 w-8 h-8 bg-purple-600 text-white rounded-full flex items-center justify-center font-bold">
                    {index + 1}
                  </span>
                  <span className="text-gray-700 pt-1">{step}</span>
                </li>
              ))}
            </ol>
          </div>
        )}

        {/* Contact Info */}
        {contact_info && (
          <div className="p-8 bg-gray-50 border-t border-gray-200">
            <h3 className="text-xl font-semibold text-gray-900 mb-4 text-center">Get in Touch</h3>
            <div className="flex flex-wrap justify-center gap-6 text-center">
              {contact_info.email && (
                <div>
                  <div className="text-2xl mb-1">📧</div>
                  <a href={`mailto:${contact_info.email}`} className="text-purple-600 hover:text-purple-700 font-medium">
                    {contact_info.email}
                  </a>
                </div>
              )}
              {contact_info.phone && (
                <div>
                  <div className="text-2xl mb-1">📞</div>
                  <a href={`tel:${contact_info.phone}`} className="text-purple-600 hover:text-purple-700 font-medium">
                    {contact_info.phone}
                  </a>
                </div>
              )}
              {contact_info.website && (
                <div>
                  <div className="text-2xl mb-1">🌐</div>
                  <a href={contact_info.website} target="_blank" rel="noopener noreferrer" className="text-purple-600 hover:text-purple-700 font-medium">
                    {contact_info.website.replace('https://', '')}
                  </a>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Lead Captured Confirmation */}
        {salesData.lead_captured && (
          <div className="p-4 bg-green-100 border-t-4 border-green-500 text-center">
            <p className="text-green-800 font-medium">
              ✓ Thanks! We've captured your information. Our team will reach out soon!
            </p>
          </div>
        )}

        {/* Back Button */}
        <div className="p-6 bg-white border-t border-gray-200 text-center">
          <button
            onClick={() => window.location.reload()}
            className="px-6 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-100 transition-colors"
          >
            ← Back to Claims
          </button>
        </div>
      </div>
    </div>
  );
};

export default SalesConversion;
