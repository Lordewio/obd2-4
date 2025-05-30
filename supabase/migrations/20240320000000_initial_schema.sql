-- Drop existing objects if they exist
drop trigger if exists on_auth_user_created on auth.users;
drop function if exists public.handle_new_user();
drop function if exists public.handle_updated_at();

drop table if exists vehicle_documents;
drop table if exists notifications;
drop table if exists maintenance_records;
drop table if exists jobs;
drop table if exists mechanics;
drop table if exists trips;
drop table if exists vehicles;
drop table if exists profiles;

drop type if exists notification_type;
drop type if exists job_status;
drop type if exists mechanic_status;
drop type if exists trip_status;
drop type if exists vehicle_status;
drop type if exists user_role;

-- Enable necessary extensions
create extension if not exists "uuid-ossp";

-- Create enum types
do $$ begin
    create type user_role as enum ('user', 'mechanic', 'fleet');
exception
    when duplicate_object then null;
end $$;

do $$ begin
    create type vehicle_status as enum ('active', 'maintenance', 'inactive');
exception
    when duplicate_object then null;
end $$;

do $$ begin
    create type trip_status as enum ('in_progress', 'completed', 'cancelled');
exception
    when duplicate_object then null;
end $$;

do $$ begin
    create type mechanic_status as enum ('available', 'busy', 'offline');
exception
    when duplicate_object then null;
end $$;

do $$ begin
    create type job_status as enum ('pending', 'accepted', 'in_progress', 'completed', 'cancelled');
exception
    when duplicate_object then null;
end $$;

do $$ begin
    create type notification_type as enum ('maintenance', 'alert', 'trip', 'job', 'system');
exception
    when duplicate_object then null;
end $$;

-- Create profiles table (extends Supabase auth.users)
create table profiles (
    id uuid references auth.users on delete cascade primary key,
    name text not null,
    email text not null unique,
    phone text,
    role user_role not null default 'user',
    created_at timestamp with time zone default timezone('utc'::text, now()) not null,
    updated_at timestamp with time zone default timezone('utc'::text, now()) not null,
    avatar_url text,
    address text,
    city text,
    state text,
    country text,
    postal_code text
);

-- Create vehicles table
create table vehicles (
    id uuid default uuid_generate_v4() primary key,
    user_id uuid references profiles(id) on delete cascade not null,
    make text not null,
    model text not null,
    year integer not null,
    vin text unique,
    license_plate text,
    status vehicle_status default 'active',
    created_at timestamp with time zone default timezone('utc'::text, now()) not null,
    updated_at timestamp with time zone default timezone('utc'::text, now()) not null,
    last_maintenance_date timestamp with time zone,
    next_maintenance_date timestamp with time zone,
    odometer_reading numeric,
    fuel_type text,
    transmission_type text
);

-- Create trips table
create table trips (
    id uuid default uuid_generate_v4() primary key,
    vehicle_id uuid references vehicles(id) on delete cascade not null,
    user_id uuid references profiles(id) on delete cascade not null,
    start_time timestamp with time zone not null,
    end_time timestamp with time zone,
    start_location point,
    end_location point,
    distance numeric,
    fuel_consumed numeric,
    status trip_status default 'in_progress',
    created_at timestamp with time zone default timezone('utc'::text, now()) not null,
    updated_at timestamp with time zone default timezone('utc'::text, now()) not null,
    average_speed numeric,
    max_speed numeric,
    harsh_braking_count integer default 0,
    harsh_acceleration_count integer default 0
);

-- Create mechanics table
create table mechanics (
    id uuid references profiles(id) on delete cascade primary key,
    status mechanic_status default 'offline',
    rating numeric default 0,
    total_jobs integer default 0,
    specialization text[],
    current_location point,
    created_at timestamp with time zone default timezone('utc'::text, now()) not null,
    updated_at timestamp with time zone default timezone('utc'::text, now()) not null,
    is_verified boolean default false,
    verification_documents text[]
);

-- Create jobs table
create table jobs (
    id uuid default uuid_generate_v4() primary key,
    vehicle_id uuid references vehicles(id) on delete cascade not null,
    user_id uuid references profiles(id) on delete cascade not null,
    mechanic_id uuid references mechanics(id) on delete cascade,
    status job_status default 'pending',
    description text not null,
    fault_codes text[],
    location point not null,
    created_at timestamp with time zone default timezone('utc'::text, now()) not null,
    updated_at timestamp with time zone default timezone('utc'::text, now()) not null,
    accepted_at timestamp with time zone,
    started_at timestamp with time zone,
    completed_at timestamp with time zone,
    estimated_cost numeric,
    actual_cost numeric,
    rating integer,
    review text
);

-- Create maintenance_records table
create table maintenance_records (
    id uuid default uuid_generate_v4() primary key,
    vehicle_id uuid references vehicles(id) on delete cascade not null,
    job_id uuid references jobs(id) on delete cascade,
    maintenance_type text not null,
    description text,
    cost numeric,
    date timestamp with time zone not null,
    created_at timestamp with time zone default timezone('utc'::text, now()) not null,
    updated_at timestamp with time zone default timezone('utc'::text, now()) not null,
    next_due_date timestamp with time zone,
    odometer_reading numeric
);

-- Create notifications table
create table notifications (
    id uuid default uuid_generate_v4() primary key,
    user_id uuid references profiles(id) on delete cascade not null,
    type notification_type not null,
    title text not null,
    message text not null,
    is_read boolean default false,
    created_at timestamp with time zone default timezone('utc'::text, now()) not null,
    updated_at timestamp with time zone default timezone('utc'::text, now()) not null,
    related_entity_id uuid,
    related_entity_type text
);

-- Create vehicle_documents table
create table vehicle_documents (
    id uuid default uuid_generate_v4() primary key,
    vehicle_id uuid references vehicles(id) on delete cascade not null,
    document_type text not null,
    document_url text not null,
    expiry_date timestamp with time zone,
    created_at timestamp with time zone default timezone('utc'::text, now()) not null,
    updated_at timestamp with time zone default timezone('utc'::text, now()) not null,
    is_verified boolean default false
);

-- Create RLS policies
alter table profiles enable row level security;
alter table vehicles enable row level security;
alter table trips enable row level security;
alter table mechanics enable row level security;
alter table jobs enable row level security;
alter table maintenance_records enable row level security;
alter table notifications enable row level security;
alter table vehicle_documents enable row level security;

-- Profiles policies
create policy "Users can view their own profile"
    on profiles for select
    using (auth.uid() = id);

create policy "Users can update their own profile"
    on profiles for update
    using (auth.uid() = id);

-- Vehicles policies
create policy "Users can view their own vehicles"
    on vehicles for select
    using (auth.uid() = user_id);

create policy "Users can insert their own vehicles"
    on vehicles for insert
    with check (auth.uid() = user_id);

create policy "Users can update their own vehicles"
    on vehicles for update
    using (auth.uid() = user_id);

-- Trips policies
create policy "Users can view their own trips"
    on trips for select
    using (auth.uid() = user_id);

create policy "Users can insert their own trips"
    on trips for insert
    with check (auth.uid() = user_id);

create policy "Users can update their own trips"
    on trips for update
    using (auth.uid() = user_id);

-- Mechanics policies
create policy "Anyone can view mechanics"
    on mechanics for select
    using (true);

create policy "Mechanics can update their own profile"
    on mechanics for update
    using (auth.uid() = id);

-- Jobs policies
create policy "Users can view their own jobs"
    on jobs for select
    using (auth.uid() = user_id);

create policy "Mechanics can view assigned jobs"
    on jobs for select
    using (auth.uid() = mechanic_id);

create policy "Users can create jobs"
    on jobs for insert
    with check (auth.uid() = user_id);

create policy "Users can update their own jobs"
    on jobs for update
    using (auth.uid() = user_id);

create policy "Mechanics can update assigned jobs"
    on jobs for update
    using (auth.uid() = mechanic_id);

-- Maintenance records policies
create policy "Users can view their vehicle maintenance records"
    on maintenance_records for select
    using (
        exists (
            select 1 from vehicles
            where vehicles.id = maintenance_records.vehicle_id
            and vehicles.user_id = auth.uid()
        )
    );

create policy "Users can insert maintenance records"
    on maintenance_records for insert
    with check (
        exists (
            select 1 from vehicles
            where vehicles.id = maintenance_records.vehicle_id
            and vehicles.user_id = auth.uid()
        )
    );

create policy "Users can update their maintenance records"
    on maintenance_records for update
    using (
        exists (
            select 1 from vehicles
            where vehicles.id = maintenance_records.vehicle_id
            and vehicles.user_id = auth.uid()
        )
    );

-- Notifications policies
create policy "Users can view their own notifications"
    on notifications for select
    using (auth.uid() = user_id);

create policy "Users can update their own notifications"
    on notifications for update
    using (auth.uid() = user_id);

-- Vehicle documents policies
create policy "Users can view their vehicle documents"
    on vehicle_documents for select
    using (
        exists (
            select 1 from vehicles
            where vehicles.id = vehicle_documents.vehicle_id
            and vehicles.user_id = auth.uid()
        )
    );

create policy "Users can insert vehicle documents"
    on vehicle_documents for insert
    with check (
        exists (
            select 1 from vehicles
            where vehicles.id = vehicle_documents.vehicle_id
            and vehicles.user_id = auth.uid()
        )
    );

create policy "Users can update their vehicle documents"
    on vehicle_documents for update
    using (
        exists (
            select 1 from vehicles
            where vehicles.id = vehicle_documents.vehicle_id
            and vehicles.user_id = auth.uid()
        )
    );

-- Create updated_at trigger function
create or replace function public.handle_updated_at()
returns trigger as $$
begin
    new.updated_at = timezone('utc'::text, now());
    return new;
end;
$$ language plpgsql security definer;

-- Create updated_at triggers for all tables
create trigger handle_updated_at_profiles
    before update on profiles
    for each row execute procedure public.handle_updated_at();

create trigger handle_updated_at_vehicles
    before update on vehicles
    for each row execute procedure public.handle_updated_at();

create trigger handle_updated_at_trips
    before update on trips
    for each row execute procedure public.handle_updated_at();

create trigger handle_updated_at_mechanics
    before update on mechanics
    for each row execute procedure public.handle_updated_at();

create trigger handle_updated_at_jobs
    before update on jobs
    for each row execute procedure public.handle_updated_at();

create trigger handle_updated_at_maintenance_records
    before update on maintenance_records
    for each row execute procedure public.handle_updated_at();

create trigger handle_updated_at_notifications
    before update on notifications
    for each row execute procedure public.handle_updated_at();

create trigger handle_updated_at_vehicle_documents
    before update on vehicle_documents
    for each row execute procedure public.handle_updated_at();

-- Create indexes
create index idx_vehicles_user_id on vehicles(user_id);
create index idx_trips_vehicle_id on trips(vehicle_id);
create index idx_trips_user_id on trips(user_id);
create index idx_jobs_vehicle_id on jobs(vehicle_id);
create index idx_jobs_user_id on jobs(user_id);
create index idx_jobs_mechanic_id on jobs(mechanic_id);
create index idx_maintenance_records_vehicle_id on maintenance_records(vehicle_id);
create index idx_notifications_user_id on notifications(user_id);
create index idx_vehicle_documents_vehicle_id on vehicle_documents(vehicle_id);

-- Create functions
create or replace function public.handle_new_user()
returns trigger as $$
begin
    insert into public.profiles (id, name, email, role)
    values (new.id, new.raw_user_meta_data->>'name', new.email, (new.raw_user_meta_data->>'role')::user_role);
    return new;
end;
$$ language plpgsql security definer;

-- Create trigger for new user
create trigger on_auth_user_created
    after insert on auth.users
    for each row execute procedure public.handle_new_user(); 