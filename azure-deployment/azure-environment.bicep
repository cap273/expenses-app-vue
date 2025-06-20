param location string = resourceGroup().location
param appName string
param appServicePlanName string
param flaskEnvironment string
param sqlServerName string
param sqlDatabaseName string
param testSqlDatabaseName string
param sqlAdministratorLogin string
param repoUrl string
param allowedIpAddresses array
@secure()
param sqlAdministratorPassword string
@secure()
param flaskSecretKey string

// SQL database initialization scripts
var createExpensesTableScript = '''
  CREATE TABLE expenses (
    ExpenseID INT PRIMARY KEY IDENTITY,
    ScopeID INT NOT NULL, -- Change from accountID to scope ID
    PersonID INT, -- Foreign key to the persons table, NULL if it's a joint expense
    Day INT,
    Month NVARCHAR(50),
    Year INT,
    ExpenseDate DATE,
    ExpenseDayOfWeek NVARCHAR(50),
    Amount FLOAT NOT NULL, -- Original unadjusted amount
    AdjustedAmount FLOAT, -- Amount after adjustments like reimbursements
    ExpenseCategory NVARCHAR(255),
    AdditionalNotes NVARCHAR(255),
    CreateDate DATE,
    LastUpdated DATE,
    Currency NVARCHAR(50), -- Currency of the transaction
    SuggestedCategory NVARCHAR(255), -- Category suggested by the ML model
    CategoryConfirmed BIT, -- Indicates if the user confirmed the ML-suggested category
    MerchantName NVARCHAR(255), -- Unified merchant name field for both manual and Plaid expenses
    SourceType NVARCHAR(10) CHECK (SourceType IN ('manual', 'plaid')), -- Source type enum
    IsIncome BIT DEFAULT 0, -- Indicates if this is an income transaction

    -- Fields added to support Plaid data:
    PlaidAccountID NVARCHAR(255),                           -- Stores Plaid's "account_id"
    PlaidTransactionID NVARCHAR(255),                       -- Stores Plaid's "transaction_id"
    PlaidTransactionType NVARCHAR(255),                     -- Stores Plaid's "transaction_type"
    PlaidCategoryID NVARCHAR(255),                          -- Stores Plaid's "category_id"

    PlaidAuthorizedDate DATE,                               -- Stores Plaid's "authorized_date"
    PlaidDate DATE,                                         -- Stores Plaid's "date"

    PlaidAmount FLOAT,                                      -- Stores Plaid's "amount"
    PlaidCurrencyCode NVARCHAR(10),                         -- Stores Plaid's "iso_currency_code"

    PlaidMerchantLogoURL NVARCHAR(255),                     -- Stores Plaid's "logo_url" 
    PlaidMerchantEntityID NVARCHAR(255),                    -- Stores Plaid's "merchant_entity_id" 
    PlaidMerchantName NVARCHAR(255),                        -- Stores Plaid's "merchant_name" 
    PlaidName NVARCHAR(255),                                -- Stores Plaid's "name" 
    PlaidPending BIT,                                       -- Stores Plaid's "pending" status
    PlaidPendingTransactionID NVARCHAR(255),                -- Stores Plaid's "pending_transaction_id"

    PlaidPersonalFinanceCategoryConfidence NVARCHAR(255),   -- Stores Plaid's "personal_finance_category - confidence_level"
    PlaidPersonalFinanceCategoryDetailed NVARCHAR(255),     -- Stores Plaid's "personal_finance_category - detailed"
    PlaidPersonalFinanceCategoryPrimary NVARCHAR(255),      -- Stores Plaid's "personal_finance_category - primary"
    PlaidPersonalFinanceCategoryIconURL NVARCHAR(255),      -- Stores Plaid's "personal_finance_category - icon_rl

    FOREIGN KEY (ScopeID) REFERENCES scopes(ScopeID),
    FOREIGN KEY (PersonID) REFERENCES persons(PersonID)
  );
'''

var createCategoriesTableScript = '''
  CREATE TABLE categories (
    CategoryID INT PRIMARY KEY IDENTITY,
    CategoryName NVARCHAR(255) UNIQUE NOT NULL,
    CreateDate DATE,
    LastUpdated DATE
  );
'''

var createAccountsTableScript = '''
  CREATE TABLE accounts (
    AccountID INT PRIMARY KEY IDENTITY,
    AccountName NVARCHAR(255) NOT NULL,
    UserEmail NVARCHAR(255) UNIQUE,
    Password NVARCHAR(255),
    AccountDisplayName NVARCHAR(255),
    Currency NVARCHAR(255),
    CreateDate DATE,
    LastUpdated DATE,
    LastLoginDate DATE
  );
'''

var createPersonsTableScript = '''
  CREATE TABLE persons (
    PersonID INT PRIMARY KEY IDENTITY,
    AccountID INT NOT NULL, -- Link to the Account table
    PersonName NVARCHAR(255) NOT NULL,
    CreateDate DATE,
    LastUpdated DATE,
    FOREIGN KEY (AccountID) REFERENCES accounts(AccountID) -- Foreign key to ensure referential integrity
  );
'''

var createTriggersForDateTrackingScript = '''
  -- Trigger for the 'expenses' table for new records
  CREATE TRIGGER trg_expenses_insert
  ON expenses
  AFTER INSERT
  AS
  BEGIN
      UPDATE expenses
      SET CreateDate = CAST(GETDATE() AS DATE),
          LastUpdated = CAST(GETDATE() AS DATE)
      FROM expenses
      INNER JOIN inserted i ON expenses.ExpenseID = i.ExpenseID
  END;
  GO

  -- Trigger for the 'expenses' table for updates
  CREATE TRIGGER trg_expenses_update
  ON expenses
  AFTER UPDATE
  AS
  BEGIN
      UPDATE expenses
      SET LastUpdated = CAST(GETDATE() AS DATE)
      FROM expenses
      INNER JOIN inserted i ON expenses.ExpenseID = i.ExpenseID
  END;
  GO

  -- Trigger for the 'categories' table for new records
  CREATE TRIGGER trg_categories_insert
  ON categories
  AFTER INSERT
  AS
  BEGIN
      UPDATE categories
      SET CreateDate = CAST(GETDATE() AS DATE),
          LastUpdated = CAST(GETDATE() AS DATE)
      FROM categories
      INNER JOIN inserted i ON categories.CategoryID = i.CategoryID
  END;
  GO

  -- Trigger for the 'categories' table for updates
  CREATE TRIGGER trg_categories_update
  ON categories
  AFTER UPDATE
  AS
  BEGIN
      UPDATE categories
      SET LastUpdated = CAST(GETDATE() AS DATE)
      FROM categories
      INNER JOIN inserted i ON categories.CategoryID = i.CategoryID
  END;
  GO

  CREATE TRIGGER trg_expenses_insert_dayofweek
  ON expenses
  AFTER INSERT
  AS
  BEGIN
      UPDATE e
      SET e.ExpenseDayOfWeek = DATENAME(dw, i.ExpenseDate)
      FROM expenses e
      INNER JOIN inserted i ON e.ExpenseID = i.ExpenseID
  END;
  GO

  -- Trigger for the 'accounts' table for new records
  CREATE TRIGGER trg_accounts_insert
  ON accounts
  AFTER INSERT
  AS
  BEGIN
      UPDATE accounts
      SET CreateDate = CAST(GETDATE() AS DATE),
          LastUpdated = CAST(GETDATE() AS DATE)
      FROM accounts
      INNER JOIN inserted i ON accounts.AccountID = i.AccountID
  END;
  GO

  -- Trigger for the 'accounts' table for updates
  CREATE TRIGGER trg_accounts_update
  ON accounts
  AFTER UPDATE
  AS
  BEGIN
      UPDATE accounts
      SET LastUpdated = CAST(GETDATE() AS DATE)
      FROM accounts
      INNER JOIN inserted i ON accounts.AccountID = i.AccountID
  END;
  GO

  -- Trigger for the 'persons' table for new records
  CREATE TRIGGER trg_persons_insert
  ON persons
  AFTER INSERT
  AS
  BEGIN
      UPDATE persons
      SET CreateDate = CAST(GETDATE() AS DATE),
          LastUpdated = CAST(GETDATE() AS DATE)
      FROM persons
      INNER JOIN inserted i ON persons.PersonID = i.PersonID
  END;
  GO

  -- Trigger for the 'persons' table for updates
  CREATE TRIGGER trg_persons_update
  ON persons
  AFTER UPDATE
  AS
  BEGIN
      UPDATE persons
      SET LastUpdated = CAST(GETDATE() AS DATE)
      FROM persons
      INNER JOIN inserted i ON persons.PersonID = i.PersonID
  END;
  GO
'''
// Add new table creation scripts for scopes and scope_access
var createScopesTableScript = '''
  CREATE TABLE scopes (
    ScopeID INT PRIMARY KEY IDENTITY,
    ScopeName NVARCHAR(255) NOT NULL,
    ScopeType NVARCHAR(50) NOT NULL, -- 'personal' or 'household'
    CreateDate DATE,
    LastUpdated DATE
  );
'''

var createScopeAccessTableScript = '''
  CREATE TABLE scope_access (
    AccessID INT PRIMARY KEY IDENTITY,
    ScopeID INT NOT NULL,
    AccountID INT NOT NULL,
    AccessType NVARCHAR(50) NOT NULL, -- 'owner' or 'member'
    InviteStatus NVARCHAR(50) NOT NULL, -- 'pending', 'accepted', 'rejected'
    CreateDate DATE,
    LastUpdated DATE,
    FOREIGN KEY (ScopeID) REFERENCES scopes(ScopeID),
    FOREIGN KEY (AccountID) REFERENCES accounts(AccountID)
  );
'''

// Add triggers for the new tables
var additionalTriggers = '''
  -- Trigger for the 'scopes' table for new records
  CREATE TRIGGER trg_scopes_insert
  ON scopes
  AFTER INSERT
  AS
  BEGIN
      UPDATE scopes
      SET CreateDate = CAST(GETDATE() AS DATE),
          LastUpdated = CAST(GETDATE() AS DATE)
      FROM scopes
      INNER JOIN inserted i ON scopes.ScopeID = i.ScopeID
  END;
  GO

  -- Trigger for the 'scopes' table for updates
  CREATE TRIGGER trg_scopes_update
  ON scopes
  AFTER UPDATE
  AS
  BEGIN
      UPDATE scopes
      SET LastUpdated = CAST(GETDATE() AS DATE)
      FROM scopes
      INNER JOIN inserted i ON scopes.ScopeID = i.ScopeID
  END;
  GO

  -- Trigger for the 'scope_access' table for new records
  CREATE TRIGGER trg_scope_access_insert
  ON scope_access
  AFTER INSERT
  AS
  BEGIN
      UPDATE scope_access
      SET CreateDate = CAST(GETDATE() AS DATE),
          LastUpdated = CAST(GETDATE() AS DATE)
      FROM scope_access
      INNER JOIN inserted i ON scope_access.AccessID = i.AccessID
  END;
  GO

  -- Trigger for the 'scope_access' table for updates
  CREATE TRIGGER trg_scope_access_update
  ON scope_access
  AFTER UPDATE
  AS
  BEGIN
      UPDATE scope_access
      SET LastUpdated = CAST(GETDATE() AS DATE)
      FROM scope_access
      INNER JOIN inserted i ON scope_access.AccessID = i.AccessID
  END;
  GO
'''

resource appServicePlan 'Microsoft.Web/serverfarms@2022-09-01' = {
  name: appServicePlanName
  location: location
  kind: 'linux'
  properties: {
    reserved: true
  }
  sku: {
    name: 'B1'
    tier: 'Basic'
  }
}

resource appService 'Microsoft.Web/sites@2022-09-01' = {
  name: appName
  location: location
  properties: {
    serverFarmId: appServicePlan.id
    siteConfig: {
      appSettings: [
        {
          name: 'DB_SERVER'
            value: '${sqlServerName}${environment().suffixes.sqlServerHostname}'
        }
        {
          name: 'DB_NAME'
          value: sqlDatabaseName
        }
        {
          name: 'DB_USERNAME'
          value: sqlAdministratorLogin
        }
        {
          name: 'DB_PASSWORD'
          value: sqlAdministratorPassword
        }
        {
          name: 'FLASK_ENV'
          value: flaskEnvironment
        }
        {
          name: 'FLASK_SECRET_KEY'
          value: flaskSecretKey
        }
      ]
      linuxFxVersion: 'Python|3.12'
      alwaysOn: false
      ftpsState: 'FtpsOnly'
      minTlsVersion:'1.2'
      http20Enabled: true
    }
  }
  dependsOn: [
    sqlDatabase
  ]
}

resource appServiceSourceControl 'Microsoft.Web/sites/sourcecontrols@2022-09-01' = {
  parent: appService
  name: 'web'
  properties: {
    repoUrl: repoUrl
    branch: 'main'
    isManualIntegration: false
    isMercurial: false
    deploymentRollbackEnabled: false
  }
}

resource sqlServer 'Microsoft.Sql/servers@2022-05-01-preview' = {
  name: sqlServerName
  location: location
  properties: {
    administratorLogin: sqlAdministratorLogin
    administratorLoginPassword: sqlAdministratorPassword
  }
}

resource sqlDatabase 'Microsoft.Sql/servers/databases@2022-05-01-preview' = {
  parent: sqlServer
  name: sqlDatabaseName
  location: location
  sku: {
    name: 'GP_S_Gen5_1'
    tier: 'GeneralPurpose'
  }
}

resource sqlDeploymentScript 'Microsoft.Resources/deploymentScripts@2020-10-01' = {
  name: 'InitializeSQLDatabase'
  location: location
  kind: 'AzurePowerShell'
  properties: {
    azPowerShellVersion: '11.0'
    retentionInterval: 'P1D' // Retain for 1 day
    scriptContent: '''
      # Install and import the SqlServer module
      Install-Module -Name SqlServer -Scope CurrentUser -Force -AllowClobber
      Import-Module SqlServer

      # PowerShell script to run the SQL scripts directly using environment variables
      # Order of execution (due to foreign key constraints: createCategoriesTableScript, createAccountsTableScript, createPersonsTableScript, createExpensesTableScript)
      Invoke-Sqlcmd -ServerInstance $env:sqlServerName -Database $env:sqlDatabaseName -Username $env:sqlAdminUsername -Password $env:sqlAdminPassword -Query $env:createCategoriesTableScript
      Invoke-Sqlcmd -ServerInstance $env:sqlServerName -Database $env:sqlDatabaseName -Username $env:sqlAdminUsername -Password $env:sqlAdminPassword -Query $env:createAccountsTableScript
      Invoke-Sqlcmd -ServerInstance $env:sqlServerName -Database $env:sqlDatabaseName -Username $env:sqlAdminUsername -Password $env:sqlAdminPassword -Query $env:createPersonsTableScript
      Invoke-Sqlcmd -ServerInstance $env:sqlServerName -Database $env:sqlDatabaseName -Username $env:sqlAdminUsername -Password $env:sqlAdminPassword -Query $env:createScopesTableScript
      Invoke-Sqlcmd -ServerInstance $env:sqlServerName -Database $env:sqlDatabaseName -Username $env:sqlAdminUsername -Password $env:sqlAdminPassword -Query $env:createScopeAccessTableScript
      Invoke-Sqlcmd -ServerInstance $env:sqlServerName -Database $env:sqlDatabaseName -Username $env:sqlAdminUsername -Password $env:sqlAdminPassword -Query $env:createExpensesTableScript
      Invoke-Sqlcmd -ServerInstance $env:sqlServerName -Database $env:sqlDatabaseName -Username $env:sqlAdminUsername -Password $env:sqlAdminPassword -Query $env:createTriggersForDateTrackingScript
      Invoke-Sqlcmd -ServerInstance $env:sqlServerName -Database $env:sqlDatabaseName -Username $env:sqlAdminUsername -Password $env:sqlAdminPassword -Query $env:additionalTriggers
    '''
    timeout: 'PT1H'
    cleanupPreference: 'OnSuccess'
    environmentVariables: [
      {
        name: 'sqlServerName'
        value: '${sqlServerName}${environment().suffixes.sqlServerHostname}'
      }
      {
        name: 'sqlDatabaseName'
        value: sqlDatabaseName
      }
      {
        name: 'sqlAdminUsername'
        value: sqlAdministratorLogin
      }
      {
        name: 'sqlAdminPassword'
        secureValue: sqlAdministratorPassword
      }
      {
        name: 'createExpensesTableScript'
        secureValue: createExpensesTableScript
      }
      {
        name: 'createCategoriesTableScript'
        secureValue: createCategoriesTableScript
      }
      {
        name: 'createAccountsTableScript'
        secureValue: createAccountsTableScript
      }
      {
        name: 'createPersonsTableScript'
        secureValue: createPersonsTableScript
      }
      {
        name: 'createScopesTableScript'
        secureValue: createScopesTableScript
      }
      {
        name: 'createScopeAccessTableScript'
        secureValue: createScopeAccessTableScript
      }
      {
        name: 'createTriggersForDateTrackingScript'
        secureValue: createTriggersForDateTrackingScript
      }
      {
        name: 'additionalTriggers'
        secureValue: additionalTriggers
      }
    ]
  }
  dependsOn: [
    sqlDatabase
  ]
}

// Making another instance of the SQL database (without initialization scripts) for testing purposes
resource testSqlDatabase 'Microsoft.Sql/servers/databases@2022-05-01-preview' = {
  parent: sqlServer
  name: testSqlDatabaseName
  location: location
  sku: {
    name: 'GP_S_Gen5_1'
    tier: 'GeneralPurpose'
  }
}

// Firewall rule resource
resource sqlFirewallRule 'Microsoft.Sql/servers/firewallRules@2022-05-01-preview' = [for ip in allowedIpAddresses: {
  parent: sqlServer
  name: 'Allow-${ip}'
  properties: {
    startIpAddress: ip
    endIpAddress: ip
  }
}]

// Firewall rule resource for Azure services
resource sqlAzureServicesFirewallRule 'Microsoft.Sql/servers/firewallRules@2022-05-01-preview' = {
  parent: sqlServer
  name: 'AllowAzureServices'
  properties: {
    startIpAddress: '0.0.0.0'
    endIpAddress: '0.0.0.0'
  }
}
