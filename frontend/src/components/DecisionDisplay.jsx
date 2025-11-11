import { formatCurrency, getDecisionColor, getDecisionIcon } from '../utils/helpers';

const DecisionDisplay = ({ decision, claimId }) => {
  const decisionType = decision.decision;
  const isApproved = decisionType === 'APPROVED';
  const isPartial = decisionType === 'PARTIAL';
  const isRejected = decisionType === 'REJECTED';
  const isManualReview = decisionType === 'MANUAL_REVIEW';

  return (
    <div className="max-w-4xl mx-auto p-6">
      <div className="bg-white rounded-xl shadow-lg overflow-hidden">
        {/* Header */}
        <div className={`p-8 border-b-4 ${
          isApproved ? 'bg-green-50 border-green-500' :
          isPartial ? 'bg-yellow-50 border-yellow-500' :
          isManualReview ? 'bg-orange-50 border-orange-500' :
          'bg-red-50 border-red-500'
        }`}>
          <div className="flex items-center justify-between">
            <div>
              <div className="flex items-center space-x-3 mb-2">
                <span className="text-4xl">{getDecisionIcon(decisionType)}</span>
                <h2 className="text-3xl font-bold text-gray-900">
                  {isApproved && 'Claim Approved!'}
                  {isPartial && 'Claim Partially Approved'}
                  {isManualReview && 'Under Review'}
                  {isRejected && 'Claim Rejected'}
                </h2>
              </div>
              <p className="text-gray-600">Claim ID: <span className="font-mono font-semibold">{claimId}</span></p>
            </div>
            <div className={`px-4 py-2 rounded-full border-2 ${getDecisionColor(decisionType)}`}>
              <span className="font-semibold">{decisionType}</span>
            </div>
          </div>
        </div>

        {/* Amount Summary */}
        <div className="p-8 bg-gray-50">
          <div className="grid md:grid-cols-3 gap-6">
            <div className="bg-white p-6 rounded-lg shadow-sm">
              <div className="text-sm text-gray-600 mb-1">Claimed Amount</div>
              <div className="text-2xl font-bold text-gray-900">{formatCurrency(decision.claimed_amount)}</div>
            </div>
            <div className="bg-white p-6 rounded-lg shadow-sm">
              <div className="text-sm text-gray-600 mb-1">Approved Amount</div>
              <div className={`text-2xl font-bold ${
                isApproved ? 'text-green-600' : isPartial ? 'text-yellow-600' : 'text-red-600'
              }`}>
                {formatCurrency(decision.approved_amount)}
              </div>
            </div>
            <div className="bg-white p-6 rounded-lg shadow-sm">
              <div className="text-sm text-gray-600 mb-1">You Pay</div>
              <div className="text-2xl font-bold text-gray-900">
                {formatCurrency(decision.claimed_amount - decision.approved_amount)}
              </div>
            </div>
          </div>
        </div>

        {/* Deductions Breakdown */}
        {decision.deductions && (decision.deductions.copay > 0 || decision.deductions.non_covered > 0 ||
         decision.deductions.exceeded_limits > 0 || decision.deductions.network_discount > 0) && (
          <div className="p-8 border-t border-gray-200">
            <h3 className="text-xl font-semibold text-gray-900 mb-4">Deductions Breakdown</h3>
            <div className="space-y-3">
              {decision.deductions.copay > 0 && (
                <div className="flex justify-between items-center">
                  <span className="text-gray-700">Co-pay (10%)</span>
                  <span className="font-semibold text-gray-900">{formatCurrency(decision.deductions.copay)}</span>
                </div>
              )}
              {decision.deductions.network_discount > 0 && (
                <div className="flex justify-between items-center">
                  <span className="text-gray-700 flex items-center">
                    Network Discount (20%)
                    <span className="ml-2 text-green-600">✓ Saved</span>
                  </span>
                  <span className="font-semibold text-green-600">-{formatCurrency(decision.deductions.network_discount)}</span>
                </div>
              )}
              {decision.deductions.non_covered > 0 && (
                <div className="flex justify-between items-center">
                  <span className="text-gray-700">Non-covered Items</span>
                  <span className="font-semibold text-gray-900">{formatCurrency(decision.deductions.non_covered)}</span>
                </div>
              )}
              {decision.deductions.exceeded_limits > 0 && (
                <div className="flex justify-between items-center">
                  <span className="text-gray-700">Exceeded Limits</span>
                  <span className="font-semibold text-gray-900">{formatCurrency(decision.deductions.exceeded_limits)}</span>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Rejection Reasons */}
        {decision.rejection_reasons && decision.rejection_reasons.length > 0 && (
          <div className="p-8 border-t border-gray-200 bg-red-50">
            <h3 className="text-xl font-semibold text-gray-900 mb-4 flex items-center">
              <span className="mr-2">⚠️</span> Rejection Reasons
            </h3>
            <div className="space-y-3">
              {decision.rejection_reasons.map((reason, index) => (
                <div key={index} className="bg-white p-4 rounded-lg border border-red-200">
                  <div className="flex items-start space-x-3">
                    <span className="text-red-600 font-semibold">{index + 1}.</span>
                    <div>
                      <div className="font-semibold text-gray-900">{reason.message}</div>
                      {reason.details && (
                        <div className="text-sm text-gray-600 mt-1">{reason.details}</div>
                      )}
                      <div className="text-xs text-gray-500 mt-1">
                        Category: {reason.category} | Code: {reason.code}
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}


        {/* Notes */}
        {decision.notes && (
          <div className="p-8 border-t border-gray-200">
            <h3 className="text-xl font-semibold text-gray-900 mb-4">Notes</h3>
            <p className="text-gray-700 whitespace-pre-wrap">{decision.notes}</p>
          </div>
        )}

        {/* Next Steps */}
        {decision.next_steps && (
          <div className="p-8 border-t border-gray-200 bg-blue-50">
            <h3 className="text-xl font-semibold text-gray-900 mb-4 flex items-center">
              <span className="mr-2">📋</span> Next Steps
            </h3>
            <div className="text-gray-700 whitespace-pre-wrap">{decision.next_steps}</div>
          </div>
        )}

        {/* Actions */}
        <div className="p-8 border-t border-gray-200 bg-gray-50">
          <div className="flex justify-between items-center">
            <button
              onClick={() => window.location.reload()}
              className="px-6 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-100 transition-colors"
            >
              Submit Another Claim
            </button>
            <button
              onClick={() => window.print()}
              className="px-6 py-2 bg-plum-600 text-white rounded-lg hover:bg-plum-700 transition-colors"
            >
              Download Decision Letter
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default DecisionDisplay;
