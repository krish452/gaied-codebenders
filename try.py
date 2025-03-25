import pandas as pd

data = [
    {
        "input": """{
  "rules": "",
  "extraction_fields": ["date", "effective date", "source bank", "Transactor", "Amount", "Expiration Date", "deal name"],
  "Request type description": {
    "Adjustment": {"Description": "interest adjustments and loan modifications", "Sub request types": []},
    "Closing Notice": {"Description": "Completion or closing of loan", "Sub request types": ["Reallocation Fees", "Amendment Fees", "Reallocation Principal"]},
    "Commitment Change": {"Description": "Change of loan commitment", "Sub request types": ["Cashless Roll", "Decrease", "Increase"]},
    "Fee Payment": {"Description": "Adjusting money between accounts by an entity", "Sub request types": ["Ongoing Fee", "Letter of Credit Fee"]},
    "Money-Movement-inbound": {"Description": "Wells Fargo Bank receiving money", "Sub request types": ["Principal", "Interest", "Principal + Interest", "Principal + Interest + Fee"]},
    "Money-Movement-outbound": {"Description": "Wells Fargo bank transferring money to outside entity", "Sub request types": ["Timebound", "Foreign currency"]}
  },
  "attachment content": "None",
  "Email content": "JPMORGAN CHASE BANK, N.A.\\nTo: CITI BANK\\nDate: 15-Dec-2023\\nSubject: Loan Adjustment Request\\n\\nDear Sir/Madam,\\nPlease note that ABC Corp has requested an adjustment on its loan. The deal 'ABC Corp Loan Adjustment 2023' has been modified for interest recalculation.\\nEffective date: 18-Dec-2023\\nAmount: USD 5,000,000.00\\nThank you,\\nLoan Services"
}""",
        "output": """{
  "extracted_fields": {
    "deal name": "ABC Corp Loan Adjustment 2023",
    "date": "15-Dec-2023",
    "effective date": "18-Dec-2023",
    "source bank": "JPMORGAN CHASE BANK, N.A.",
    "Transactor": "ABC Corp",
    "Amount": "USD 5,000,000.00",
    "expiration date": null
  },
  "request type": {
    "Primary Request Type": "Adjustment",
    "Request Type": [
      {
        "Adjustment": {
          "Confidence score": 0.9,
          "Reason": "Clear instruction for interest adjustment is mentioned.",
          "request sub type": null
        }
      }
    ]
  }
}"""
    },
    {
        "input": """{
  "rules": "",
  "extraction_fields": ["date", "effective date", "source bank", "Transactor", "Amount", "Expiration Date", "deal name"],
  "Request type description": {
    "Adjustment": {"Description": "interest adjustments and loan modifications", "Sub request types": []},
    "Closing Notice": {"Description": "Completion or closing of loan", "Sub request types": ["Reallocation Fees", "Amendment Fees", "Reallocation Principal"]},
    "Commitment Change": {"Description": "Change of loan commitment", "Sub request types": ["Cashless Roll", "Decrease", "Increase"]},
    "Fee Payment": {"Description": "Adjusting money between accounts by an entity", "Sub request types": ["Ongoing Fee", "Letter of Credit Fee"]},
    "Money-Movement-inbound": {"Description": "Wells Fargo Bank receiving money", "Sub request types": ["Principal", "Interest", "Principal + Interest", "Principal + Interest + Fee"]},
    "Money-Movement-outbound": {"Description": "Wells Fargo bank transferring money to outside entity", "Sub request types": ["Timebound", "Foreign currency"]}
  },
  "attachment content": "None",
  "Email content": "WELLS FARGO BANK, N.A.\\nTo: HSBC BANK\\nDate: 05-Jan-2024\\nSubject: Closing Notice for Loan\\n\\nDear Team,\\nPlease be informed that the loan for the deal 'XYZ Project Finance Deal' is now closed.\\nEffective date: 07-Jan-2024\\nAmount disbursed: USD 10,000,000.00\\nExpiration Date: 31-Dec-2024\\nRegards,\\nLoan Operations"
}""",
        "output": """{
  "extracted_fields": {
    "deal name": "XYZ Project Finance Deal",
    "date": "05-Jan-2024",
    "effective date": "07-Jan-2024",
    "source bank": "WELLS FARGO BANK, N.A.",
    "Transactor": "XYZ Ltd.",
    "Amount": "USD 10,000,000.00",
    "expiration date": "31-Dec-2024"
  },
  "request type": {
    "Primary Request Type": "Closing Notice",
    "Request Type": [
      {
        "Closing Notice": {
          "Confidence score": 0.95,
          "Reason": "Email subject and content indicate a loan closing with fee adjustments.",
          "request sub type": "Amendment Fees"
        }
      },
      {
        "Fee Payment": {
          "Confidence score": 0.3,
          "Reason": "Minor fee payment elements mentioned.",
          "request sub type": null
        }
      }
    ]
  }
}"""
    },
    {
        "input": """{
  "rules": "",
  "extraction_fields": ["date", "effective date", "source bank", "Transactor", "Amount", "Expiration Date", "deal name"],
  "Request type description": {
    "Adjustment": {"Description": "interest adjustments and loan modifications", "Sub request types": []},
    "Closing Notice": {"Description": "Completion or closing of loan", "Sub request types": ["Reallocation Fees", "Amendment Fees", "Reallocation Principal"]},
    "Commitment Change": {"Description": "Change of loan commitment", "Sub request types": ["Cashless Roll", "Decrease", "Increase"]},
    "Fee Payment": {"Description": "Adjusting money between accounts by an entity", "Sub request types": ["Ongoing Fee", "Letter of Credit Fee"]},
    "Money-Movement-inbound": {"Description": "Wells Fargo Bank receiving money", "Sub request types": ["Principal", "Interest", "Principal + Interest", "Principal + Interest + Fee"]},
    "Money-Movement-outbound": {"Description": "Wells Fargo bank transferring money to outside entity", "Sub request types": ["Timebound", "Foreign currency"]}
  },
  "attachment content": "None",
  "Email content": "BANK OF AMERICA, N.A.\\nTo: WELLS FARGO BANK NATIONAL ASSOCIATION\\nDate: 20-Feb-2024\\nSubject: Commitment Change Notification\\n\\nDear Partner,\\nPlease note the commitment for the deal 'DEF Finance Loan Commitment' has been updated. The principal balance reflects an increase.\\nEffective date: 22-Feb-2024\\nAmount: USD 15,000,000.00\\nRegards,\\nRelationship Manager"
}""",
        "output": """{
  "extracted_fields": {
    "deal name": "DEF Finance Loan Commitment",
    "date": "20-Feb-2024",
    "effective date": "22-Feb-2024",
    "source bank": "BANK OF AMERICA, N.A.",
    "Transactor": "DEF Finance",
    "Amount": "USD 15,000,000.00",
    "expiration date": null
  },
  "request type": {
    "Primary Request Type": "Commitment Change",
    "Request Type": [
      {
        "Commitment Change": {
          "Confidence score": 0.85,
          "Reason": "Increase in commitment indicated by updated principal balance.",
          "request sub type": "Increase"
        }
      },
      {
        "Adjustment": {
          "Confidence score": 0.15,
          "Reason": "Minor adjustment possibility.",
          "request sub type": null
        }
      }
    ]
  }
}"""
    },
    {
        "input": """{
  "rules": "",
  "extraction_fields": ["date", "effective date", "source bank", "Transactor", "Amount", "Expiration Date", "deal name"],
  "Request type description": {
    "Adjustment": {"Description": "interest adjustments and loan modifications", "Sub request types": []},
    "Closing Notice": {"Description": "Completion or closing of loan", "Sub request types": ["Reallocation Fees", "Amendment Fees", "Reallocation Principal"]},
    "Commitment Change": {"Description": "Change of loan commitment", "Sub request types": ["Cashless Roll", "Decrease", "Increase"]},
    "Fee Payment": {"Description": "Adjusting money between accounts by an entity", "Sub request types": ["Ongoing Fee", "Letter of Credit Fee"]},
    "Money-Movement-inbound": {"Description": "Wells Fargo Bank receiving money", "Sub request types": ["Principal", "Interest", "Principal + Interest", "Principal + Interest + Fee"]},
    "Money-Movement-outbound": {"Description": "Wells Fargo bank transferring money to outside entity", "Sub request types": ["Timebound", "Foreign currency"]}
  },
  "attachment content": "None",
  "Email content": "HSBC BANK\\nTo: JPMORGAN CHASE BANK\\nDate: 25-Apr-2024\\nSubject: Inbound Fund Movement Confirmation\\n\\nDear Team,\\nThis is to confirm the receipt of funds for the deal 'JKL Funding Deal'. The payment includes both principal and interest components.\\nEffective date: 27-Apr-2024\\nAmount: USD 8,000,000.00\\nThank you,\\nTreasury Dept."
}""",
        "output": """{
  "extracted_fields": {
    "deal name": "JKL Funding Deal",
    "date": "25-Apr-2024",
    "effective date": "27-Apr-2024",
    "source bank": "HSBC BANK",
    "Transactor": "JKL Inc.",
    "Amount": "USD 8,000,000.00",
    "expiration date": null
  },
  "request type": {
    "Primary Request Type": "Money-Movement-inbound",
    "Request Type": [
      {
        "Money-Movement-inbound": {
          "Confidence score": 0.88,
          "Reason": "Payment includes both principal and interest as specified.",
          "request sub type": "Principal + Interest"
        }
      },
      {
        "Adjustment": {
          "Confidence score": 0.12,
          "Reason": "Possible adjustment consideration.",
          "request sub type": null
        }
      }
    ]
  }
}"""
    },
    {
        "input": """{
  "rules": "",
  "extraction_fields": ["date", "effective date", "source bank", "Transactor", "Amount", "Expiration Date", "deal name"],
  "Request type description": {
    "Adjustment": {"Description": "interest adjustments and loan modifications", "Sub request types": []},
    "Closing Notice": {"Description": "Completion or closing of loan", "Sub request types": ["Reallocation Fees", "Amendment Fees", "Reallocation Principal"]},
    "Commitment Change": {"Description": "Change of loan commitment", "Sub request types": ["Cashless Roll", "Decrease", "Increase"]},
    "Fee Payment": {"Description": "Adjusting money between accounts by an entity", "Sub request types": ["Ongoing Fee", "Letter of Credit Fee"]},
    "Money-Movement-inbound": {"Description": "Wells Fargo Bank receiving money", "Sub request types": ["Principal", "Interest", "Principal + Interest", "Principal + Interest + Fee"]},
    "Money-Movement-outbound": {"Description": "Wells Fargo bank transferring money to outside entity", "Sub request types": ["Timebound", "Foreign currency"]}
  },
  "attachment content": "None",
  "Email content": "WELLS FARGO BANK\\nTo: BARCLAYS BANK\\nDate: 30-May-2024\\nSubject: Outbound Fund Transfer Notification\\n\\nDear Client,\\nWe are processing an outbound transfer for the deal 'MNO Export Finance Deal'. The funds will be transferred in foreign currency.\\nEffective date: 01-Jun-2024\\nAmount: USD 12,000,000.00\\nExpiration Date: 30-Jun-2024\\nRegards,\\nOperations"
}""",
        "output": """{
  "extracted_fields": {
    "deal name": "MNO Export Finance Deal",
    "date": "30-May-2024",
    "effective date": "01-Jun-2024",
    "source bank": "WELLS FARGO BANK",
    "Transactor": "MNO Exports",
    "Amount": "USD 12,000,000.00",
    "expiration date": "30-Jun-2024"
  },
  "request type": {
    "Primary Request Type": "Money-Movement-outbound",
    "Request Type": [
      {
        "Money-Movement-outbound": {
          "Confidence score": 0.75,
          "Reason": "Funds are being transferred in foreign currency.",
          "request sub type": "Foreign currency"
        }
      },
      {
        "Money-Movement-outbound": {
          "Confidence score": 0.25,
          "Reason": "Alternative possibility of timebound transfer.",
          "request sub type": "Timebound"
        }
      }
    ]
  }
}"""
    },
    {
        "input": """{
  "rules": "",
  "extraction_fields": ["date", "effective date", "source bank", "Transactor", "Amount", "Expiration Date", "deal name"],
  "Request type description": {
    "Adjustment": {"Description": "interest adjustments and loan modifications", "Sub request types": []},
    "Closing Notice": {"Description": "Completion or closing of loan", "Sub request types": ["Reallocation Fees", "Amendment Fees", "Reallocation Principal"]},
    "Commitment Change": {"Description": "Change of loan commitment", "Sub request types": ["Cashless Roll", "Decrease", "Increase"]},
    "Fee Payment": {"Description": "Adjusting money between accounts by an entity", "Sub request types": ["Ongoing Fee", "Letter of Credit Fee"]},
    "Money-Movement-inbound": {"Description": "Wells Fargo Bank receiving money", "Sub request types": ["Principal", "Interest", "Principal + Interest", "Principal + Interest + Fee"]},
    "Money-Movement-outbound": {"Description": "Wells Fargo bank transferring money to outside entity", "Sub request types": ["Timebound", "Foreign currency"]}
  },
  "attachment content": "None",
  "Email content": "SANTANDER BANK\\nTo: CREDIT SUISSE\\nDate: 05-Jul-2024\\nSubject: Loan Adjustment Request\\n\\nDear Sir/Madam,\\nKindly note the adjustment request for 'PQR Adjustable Rate Loan'. The interest recalculation needs to be applied.\\nEffective date: 06-Jul-2024\\nAmount: USD 2,000,000.00\\nThank you,\\nLoan Processing Unit"
}""",
        "output": """{
  "extracted_fields": {
    "deal name": "PQR Adjustable Rate Loan",
    "date": "05-Jul-2024",
    "effective date": "06-Jul-2024",
    "source bank": "SANTANDER BANK",
    "Transactor": "PQR Corp",
    "Amount": "USD 2,000,000.00",
    "expiration date": null
  },
  "request type": {
    "Primary Request Type": "Adjustment",
    "Request Type": [
      {
        "Adjustment": {
          "Confidence score": 0.92,
          "Reason": "The email specifies an interest recalculation adjustment.",
          "request sub type": null
        }
      }
    ]
  }
}"""
    },
    {
        "input": """{
  "rules": "",
  "extraction_fields": ["date", "effective date", "source bank", "Transactor", "Amount", "Expiration Date", "deal name"],
  "Request type description": {
    "Adjustment": {"Description": "interest adjustments and loan modifications", "Sub request types": []},
    "Closing Notice": {"Description": "Completion or closing of loan", "Sub request types": ["Reallocation Fees", "Amendment Fees", "Reallocation Principal"]},
    "Commitment Change": {"Description": "Change of loan commitment", "Sub request types": ["Cashless Roll", "Decrease", "Increase"]},
    "Fee Payment": {"Description": "Adjusting money between accounts by an entity", "Sub request types": ["Ongoing Fee", "Letter of Credit Fee"]},
    "Money-Movement-inbound": {"Description": "Wells Fargo Bank receiving money", "Sub request types": ["Principal", "Interest", "Principal + Interest", "Principal + Interest + Fee"]},
    "Money-Movement-outbound": {"Description": "Wells Fargo bank transferring money to outside entity", "Sub request types": ["Timebound", "Foreign currency"]}
  },
  "attachment content": "None",
  "Email content": "DEUTSCHE BANK\\nTo: WELLS FARGO BANK\\nDate: 15-Aug-2024\\nSubject: Closing Notice: Final Settlement\\n\\nDear Colleague,\\nThe deal 'STU Bridge Loan' has reached its final settlement. Please note the reallocation of principal as part of the closing process.\\nEffective date: 17-Aug-2024\\nAmount: USD 25,000,000.00\\nExpiration Date: 15-Oct-2024\\nBest regards,\\nSettlement Team"
}""",
        "output": """{
  "extracted_fields": {
    "deal name": "STU Bridge Loan",
    "date": "15-Aug-2024",
    "effective date": "17-Aug-2024",
    "source bank": "DEUTSCHE BANK",
    "Transactor": "STU Investments",
    "Amount": "USD 25,000,000.00",
    "expiration date": "15-Oct-2024"
  },
  "request type": {
    "Primary Request Type": "Closing Notice",
    "Request Type": [
      {
        "Closing Notice": {
          "Confidence score": 0.87,
          "Reason": "Final settlement and principal reallocation indicated.",
          "request sub type": "Reallocation Principal"
        }
      },
      {
        "Fee Payment": {
          "Confidence score": 0.1,
          "Reason": "Minor fee payment element.",
          "request sub type": null
        }
      }
    ]
  }
}"""
    },
    {
        "input": """{
  "rules": "",
  "extraction_fields": ["date", "effective date", "source bank", "Transactor", "Amount", "Expiration Date", "deal name"],
  "Request type description": {
    "Adjustment": {"Description": "interest adjustments and loan modifications", "Sub request types": []},
    "Closing Notice": {"Description": "Completion or closing of loan", "Sub request types": ["Reallocation Fees", "Amendment Fees", "Reallocation Principal"]},
    "Commitment Change": {"Description": "Change of loan commitment", "Sub request types": ["Cashless Roll", "Decrease", "Increase"]},
    "Fee Payment": {"Description": "Adjusting money between accounts by an entity", "Sub request types": ["Ongoing Fee", "Letter of Credit Fee"]},
    "Money-Movement-inbound": {"Description": "Wells Fargo Bank receiving money", "Sub request types": ["Principal", "Interest", "Principal + Interest", "Principal + Interest + Fee"]},
    "Money-Movement-outbound": {"Description": "Wells Fargo bank transferring money to outside entity", "Sub request types": ["Timebound", "Foreign currency"]}
  },
  "attachment content": "None",
  "Email content": "UBS BANK\\nTo: GOLDMAN SACHS\\nDate: 22-Sep-2024\\nSubject: Commitment Change Notice\\n\\nDear Partner,\\nWe wish to notify you of a decrease in the loan commitment for the deal 'VWX Corporate Loan'.\\nEffective date: 24-Sep-2024\\nAmount: USD 30,000,000.00\\nRegards,\\nCredit Department"
}""",
        "output": """{
  "extracted_fields": {
    "deal name": "VWX Corporate Loan",
    "date": "22-Sep-2024",
    "effective date": "24-Sep-2024",
    "source bank": "UBS BANK",
    "Transactor": "VWX Corp",
    "Amount": "USD 30,000,000.00",
    "expiration date": null
  },
  "request type": {
    "Primary Request Type": "Commitment Change",
    "Request Type": [
      {
        "Commitment Change": {
          "Confidence score": 0.95,
          "Reason": "The email clearly states a decrease in commitment.",
          "request sub type": "Decrease"
        }
      },
      {
        "Adjustment": {
          "Confidence score": 0.05,
          "Reason": "Minor adjustment possibility.",
          "request sub type": null
        }
      }
    ]
  }
}"""
    },
    {
        "input": """{
  "rules": "",
  "extraction_fields": ["date", "effective date", "source bank", "Transactor", "Amount", "Expiration Date", "deal name"],
  "Request type description": {
    "Adjustment": {"Description": "interest adjustments and loan modifications", "Sub request types": []},
    "Closing Notice": {"Description": "Completion or closing of loan", "Sub request types": ["Reallocation Fees", "Amendment Fees", "Reallocation Principal"]},
    "Commitment Change": {"Description": "Change of loan commitment", "Sub request types": ["Cashless Roll", "Decrease", "Increase"]},
    "Fee Payment": {"Description": "Adjusting money between accounts by an entity", "Sub request types": ["Ongoing Fee", "Letter of Credit Fee"]},
    "Money-Movement-inbound": {"Description": "Wells Fargo Bank receiving money", "Sub request types": ["Principal", "Interest", "Principal + Interest", "Principal + Interest + Fee"]},
    "Money-Movement-outbound": {"Description": "Wells Fargo bank transferring money to outside entity", "Sub request types": ["Timebound", "Foreign currency"]}
  },
  "attachment content": "None",
  "Email content": "BNP PARIBAS\\nTo: CITIBANK\\nDate: 10-Oct-2024\\nSubject: Fee Payment - Ongoing Fee Collection\\n\\nDear Finance Team,\\nPlease process the ongoing fee for the deal 'YZA Renewable Energy Loan'.\\nEffective date: 11-Oct-2024\\nAmount: USD 750,000.00\\nThank you,\\nAccounts Department"
}""",
        "output": """{
  "extracted_fields": {
    "deal name": "YZA Renewable Energy Loan",
    "date": "10-Oct-2024",
    "effective date": "11-Oct-2024",
    "source bank": "BNP PARIBAS",
    "Transactor": "YZA Energy",
    "Amount": "USD 750,000.00",
    "expiration date": null
  },
  "request type": {
    "Primary Request Type": "Fee Payment",
    "Request Type": [
      {
        "Fee Payment": {
          "Confidence score": 0.93,
          "Reason": "Ongoing fee collection mentioned clearly.",
          "request sub type": "Ongoing Fee"
        }
      }
    ]
  }
}"""
    }
]

df = pd.DataFrame(data, columns=["input", "output"])
df.to_excel("loan_samples.xlsx", index=False)