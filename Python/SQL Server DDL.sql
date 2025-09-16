

        CREATE TABLE [dbo].[tbl_DQChild] (
            [ID] [int] IDENTITY(1,1) NOT NULL,
            [Code] [varchar](250) NOT NULL,
            [Name] [varchar](250) NULL,
            [DQParent] [varchar](250) NULL,
            [IsValid] [varchar](250) NULL,
        CONSTRAINT [PK_tbl_DQChild_Code] PRIMARY KEY CLUSTERED
        (
            [Code] ASC
        )WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
        ) ON [PRIMARY]
        GO


        CREATE TABLE [dbo].[tbl_DQParent] (
            [ID] [int] IDENTITY(1,1) NOT NULL,
            [Code] [varchar](250) NOT NULL,
            [Name] [varchar](250) NULL,
            [IsValid] [varchar](250) NULL,
        CONSTRAINT [PK_tbl_DQParent_Code] PRIMARY KEY CLUSTERED
        (
            [Code] ASC
        )WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
        ) ON [PRIMARY]
        GO
