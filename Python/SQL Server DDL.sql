

        CREATE TABLE [dbo].[tbl_Test] (
            [ID] [int] IDENTITY(1,1) NOT NULL,
            [Code] [varchar](250) NOT NULL,
            [Name] [varchar](250) NULL,
            [Test2] [decimal](26,0) NULL,
            [DateAttribute] [date] NULL,
            [DBAAttribute] [varchar](250) NULL,
            [NumberAttribute] [decimal](26,2) NULL,
            [Test] [varchar](200) NULL,
            [DateTimeAttribute] [datetime2](3) NULL,
        CONSTRAINT [PK_tbl_Test_Code] PRIMARY KEY CLUSTERED
        (
            [Code] ASC
        )WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
        ) ON [PRIMARY]
        GO
