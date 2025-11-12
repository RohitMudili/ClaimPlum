import { useEffect } from 'react';
import { formatCurrency, getDecisionColor, getDecisionIcon } from '../utils/helpers';
import confirmIcon from '../assets/confirm-icon.webp';
import folderMoveIcon from '../assets/folder-move-icon.webp';

const DecisionDisplay = ({ decision, claimId, onReset }) => {
  const decisionType = decision.decision;
  const isApproved = decisionType === 'APPROVED';
  const isPartial = decisionType === 'PARTIAL';
  const isRejected = decisionType === 'REJECTED';
  const isManualReview = decisionType === 'MANUAL_REVIEW';

  // Scroll to top when component mounts
  useEffect(() => {
    window.scrollTo(0, 0);
  }, []);

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
                  <img
                    src={getDecisionIcon(decisionType)}
                    alt={`${decisionType} icon`}
                    className="w-12 h-12"
                  />
                <h2 className="text-3xl font-bold text-gray-900">
                  {isApproved && 'Claim Approved!'}
                  {isPartial && 'Claim Partially Approved'}
                  {isManualReview && 'Under Review'}
                  {isRejected && 'Claim Rejected'}
                </h2>
              </div>
              <p className="text-gray-600 ml-16">Claim ID: <span className="font-mono font-semibold">{claimId}</span></p>
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

        {/* Deductions Breakdown - Merged with Notes (Hide for REJECTED claims) */}
        {!isRejected && ((decision.deductions && (decision.deductions.copay > 0 || decision.deductions.non_covered > 0 ||
         decision.deductions.exceeded_limits > 0 || decision.deductions.network_discount > 0)) || decision.notes) && (
          <div className="p-8 border-t border-gray-200">
            <h3 className="text-xl font-semibold text-gray-900 mb-6">Deductions Breakdown</h3>

            {/* Deductions List */}
            {decision.deductions && (decision.deductions.copay > 0 || decision.deductions.non_covered > 0 ||
             decision.deductions.exceeded_limits > 0 || decision.deductions.network_discount > 0) && (
              <div className="mb-6">
                <div className="space-y-3">
                  {decision.deductions.copay > 0 && (
                    <div className="flex justify-between items-center py-2 border-b border-gray-100">
                      <span className="text-gray-700">Co-pay (10%)</span>
                      <span className="font-semibold text-gray-900">{formatCurrency(decision.deductions.copay)}</span>
                    </div>
                  )}
                  {decision.deductions.network_discount > 0 && (
                    <div className="flex justify-between items-center py-2 border-b border-gray-100">
                      <span className="text-gray-700 flex items-center">
                        Network Discount (20%)
                        <span className="ml-2 text-green-600 flex items-center gap-1">
                          <img src={confirmIcon} alt="Saved" className="w-4 h-4" />
                          Saved
                        </span>
                      </span>
                      <span className="font-semibold text-green-600">-{formatCurrency(decision.deductions.network_discount)}</span>
                    </div>
                  )}
                  {decision.deductions.non_covered > 0 && (
                    <div className="flex justify-between items-center py-2 border-b border-gray-100">
                      <span className="text-gray-700">Non-covered Items</span>
                      <span className="font-semibold text-gray-900">{formatCurrency(decision.deductions.non_covered)}</span>
                    </div>
                  )}
                  {decision.deductions.exceeded_limits > 0 && (
                    <div className="flex justify-between items-center py-2 border-b border-gray-100">
                      <span className="text-gray-700">Exceeded Limits</span>
                      <span className="font-semibold text-gray-900">{formatCurrency(decision.deductions.exceeded_limits)}</span>
                    </div>
                  )}
                </div>
              </div>
            )}

            {/* Notes Callout */}
            {decision.notes && (
              <div className="mt-6 p-5 bg-primary-50 border-l-4 border-primary-500 rounded-r-lg">
                <div className="flex items-start">
                  <svg className="w-5 h-5 text-primary-500 mr-3 mt-0.5 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
                  </svg>
                  <div className="flex-1">
                    <p className="text-sm font-medium text-primary-900 mb-1">Summary</p>
                    <p className="text-sm text-gray-700 leading-relaxed whitespace-pre-wrap">{decision.notes}</p>
                  </div>
                </div>
              </div>
            )}
          </div>
        )}

        {/* Rejection Reasons */}
        {decision.rejection_reasons && decision.rejection_reasons.length > 0 && (
          <div className="p-8 border-t border-gray-200">
            <h3 className="text-xl font-semibold text-gray-900 mb-6">
              Why This Claim Was Not Approved
            </h3>

            {/* Single Red Callout Box */}
            <div className="p-5 bg-red-50 border-l-4 border-red-500 rounded-r-lg">
              <div className="flex items-start">
                <svg className="w-5 h-5 text-red-500 mr-3 mt-0.5 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                </svg>
                <div className="flex-1">
                  <p className="text-sm font-medium text-red-900 mb-3">Rejection Reasons</p>
                  <div className="space-y-4">
                    {decision.rejection_reasons.map((reason, index) => (
                      <div key={index}>
                        <p className="text-sm font-semibold text-gray-900 mb-1">
                          {reason.message}
                        </p>
                        {reason.details && (
                          <p className="text-sm text-gray-700 leading-relaxed">
                            {reason.details}
                          </p>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Next Steps & Actions - Combined */}
        <div className="p-8 border-t border-gray-200 bg-gray-50">
          <h3 className="text-xl font-semibold text-gray-900 mb-4 flex items-center">
            <img src={folderMoveIcon} alt="Next steps" className="w-6 h-6 mr-4" />
            Next Steps
          </h3>

          {/* Next Steps Content */}
          {decision.next_steps && (
            <div className="text-gray-700 whitespace-pre-wrap mb-6">
              {decision.next_steps}
            </div>
          )}

          {/* Action Buttons */}
          <div className="flex flex-col sm:flex-row gap-4 sm:justify-between items-stretch sm:items-center">
            <button
              onClick={onReset}
              className="px-8 py-3 bg-white border-2 border-primary-600 text-primary-600 rounded-full font-semibold hover:bg-primary-50 transition-colors"
            >
              Submit Another Claim
            </button>
            <button
              onClick={() => window.print()}
              className="px-8 py-3 bg-primary-600 text-white rounded-full font-semibold hover:bg-primary-700 transition-colors shadow-sm hover:shadow-md"
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