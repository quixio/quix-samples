namespace Quix.Redshift.Domain.Models
{
    public class OrganisationId : StringValueObject
    {

        public OrganisationId(string value) : base(value?.ToLower(), false)
        {
        }
    }
}